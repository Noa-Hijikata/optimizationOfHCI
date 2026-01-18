"""AI エージェントユースケースラッパー（A方式: APIキー）

このモジュールは google-generativeai クライアントを利用して
簡易的なチャットラッパーと、自然文コマンドの解釈・DB読み出し
（例: 昨日の申請を取得する）を提供します。

注意:
- 実行環境に `google-generativeai` がインストールされている必要があります。
- 開発では環境変数 `GOOGLE_API_KEY` を設定してください。
"""

from typing import Any, Dict, Optional
import os
import re
import logging
import json
from datetime import datetime, timedelta

from infrastructure.csvRepository import CSVLogRepository
from usecases.prompt import getPredictExpenseReportPrompt, getRefinementPrompt
from utils.utils import parse_ai_response

from google import genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class AIAgent:
    """簡易的なAIエージェントラッパー

    役割:
    - ユーザーの自然文を解析して簡易インテントを返す
    - DB（CSVログ）から最近の申請を取得して返すヘルパー
    """

    def __init__(
        self,
        log_repo: Optional[CSVLogRepository] = None,
    ):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        self.log_repo = log_repo or CSVLogRepository(log_path="data/logs.csv")

        # lazy import / configure when needed
        self._client_configured = False
        self._genai: genai.Client = None

    def interpret_command(self, text: str, history: list = None) -> str:
        """ユーザの意図を解釈した結果を返す"""
        try:
            client = genai.Client(api_key=self.api_key)
            # 利用可能なカテゴリリストを取得
            from presentation.const import CATEGORIES  # 遅延インポート

            # CATEGORIES はリストとして定義されているため keys() ではなくイテレートする
            available_categories = ", ".join([f"'{cat}'" for cat in CATEGORIES])

            prompt = getPredictExpenseReportPrompt(text, available_categories, history)
            resp = client.models.generate_content(
                model="gemini-3-flash-preview", contents=prompt
            )
            return resp.text

        except Exception as e:
            logger.exception("AI client configuration failed: %s", e)
            return "(AI error) 応答を取得できませんでした。", e

    def fetch_recent_submission(
        self, user_id: str, limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """CSVログ（`CSVLogRepository`）から最近の申請を取得する（最も新しい1件を返す）"""
        try:
            submissions = self.log_repo.get_recent_submissions(user_id, limit=limit)
            if not submissions:
                logger.info("No recent submissions found for user_id: %s", user_id)
                return None
            # assume submissions are ordered newest-first in repository
            first = submissions[0]
            if isinstance(first, dict) and "data" in first:
                return first["data"]
            return first if isinstance(first, dict) else None
        except Exception as e:
            logger.exception("Failed to fetch recent submissions: %s", e)
            return None

    def apply_intent(self, ai_resp: str, user_id: str) -> Dict[str, Any]:
        """インテントを受けてサーバー側で検索を行う

        Returns:
            {
                "status": "success" | "multiple" | "not_found",
                "data": Dict (1つに絞れた場合),
                "candidates": List (複数ある場合),
                "message": str
            }
        """
        intent = parse_ai_response(ai_resp)
        if not intent or intent.get("intent") == "unknown":
            return {"status": "not_found", "message": "意図を解釈できませんでした。"}

        # 検索条件の組み立て
        criteria = {
            "days_ago": intent.get("days_ago"),
            "category": intent.get("category"),
            "destination": intent.get("destination"),
            "amount": intent.get("amount"),
        }

        matches = self.search_submissions(user_id, criteria)

        if len(matches) == 1:
            data = matches[0]
            # 不要なキーを削除
            for key in ["user", "date", "uploaded_file"]:
                if key in data:
                    del data[key]
            return {"status": "success", "data": data}

        elif len(matches) > 1:
            return {"status": "multiple", "candidates": matches}

        else:
            return {"status": "not_found"}

    def search_submissions(self, user_id: str, criteria: Dict[str, Any]) -> list:
        """条件に合致する申請をすべて検索する"""
        all_subs = self.log_repo.get_recent_submissions(user_id, limit=20)
        matches = []

        days_ago = criteria.get("days_ago")
        category = criteria.get("category")
        destination = criteria.get("destination")
        amount = criteria.get("amount")

        for sub in all_subs:
            sub_data = sub.get("data", {})
            sub_ts = sub.get("timestamp", 0)

            # 日付フィルタ
            if days_ago is not None:
                target_ts = datetime.now().timestamp() - (days_ago * 86400)
                if abs(sub_ts - target_ts) > 43200:  # 12時間の猶予
                    continue

            # カテゴリフィルタ
            if category:
                if not (
                    self._matches_category(sub.get("category", ""), category)
                    or any(self._matches_category(k, category) for k in sub_data.keys())
                ):
                    continue

            # 目的地フィルタ
            if destination:
                target_str = (
                    str(sub_data.get("destination", ""))
                    + str(sub_data.get("arrival", ""))
                    + str(sub_data.get("departure", ""))
                ).lower()
                if destination.lower() not in target_str:
                    continue

            # 金額フィルタ
            if amount is not None:
                if sub_data.get("amount") != amount and sub_data.get("total") != amount:
                    continue

            matches.append(sub_data)
        return matches

    def generate_clarification(
        self, user_input: str, history: list, status: str, candidates: list = None
    ) -> str:
        """ユーザーに聞き返すための文言を生成する"""
        try:
            client = genai.Client(api_key=self.api_key)
            prompt = getRefinementPrompt(user_input, history, status, candidates)
            resp = client.models.generate_content(
                model="gemini-3-flash-preview", contents=prompt
            )
            return resp.text
        except Exception as e:
            logger.exception("Failed to generate clarification: %s", e)
            return "すみません、条件に合う申請を絞り込めませんでした。もう少し詳しく教えていただけますか？"

    def fetch_recent_submission_by_days(
        self, user_id: str, days_ago: int = 1, limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """指定日数前後の申請データを取得する（より柔軟）"""
        try:
            submissions = self.log_repo.get_recent_submissions(user_id, limit=limit)
            if not submissions:
                logger.info("No submissions found for user_id: %s", user_id)
                return None

            # 指定日数前のエントリを探す
            target_timestamp = datetime.now().timestamp() - (
                days_ago * 86400
            )  # 86400 = 1日のseconds

            # 最も近い日付の申請を取得
            closest = None
            min_diff = float("inf")

            for sub in submissions:
                ts = sub.get("timestamp", 0)
                diff = abs(ts - target_timestamp)
                if diff < min_diff:
                    min_diff = diff
                    closest = sub

            if closest and "data" in closest:
                return closest["data"]
            return None
        except Exception as e:
            logger.exception("Failed to fetch submission by days: %s", e)
            return None

    def _matches_category(self, field_key: str, target_category: str) -> bool:
        """フィールド名がターゲットカテゴリと一致するか判定"""
        field_key_lower = field_key.lower()
        target_lower = target_category.lower()

        category_aliases = {
            "transportation": ["transport", "交通", "taxi", "train", "bus", "flight"],
            "meal": ["食事", "food", "lunch", "breakfast", "dinner", "coffee", "cafe"],
            "business": ["業務", "work", "pc", "software", "tool", "equipment"],
            "gift": ["gift", "present", "お土産"],
        }

        # 完全一致
        if field_key_lower == target_lower:
            return True

        # エイリアスで一致
        aliases = category_aliases.get(target_category, [])
        for alias in aliases:
            if alias in field_key_lower:
                return True

        return False
