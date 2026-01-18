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
from usecases.prompt import getPredictExpenseReportPrompt

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

    def interpret_command(self, text: str) -> str:
        """ユーザの意図を解釈した結果を返す"""
        try:
            client = genai.Client(api_key=self.api_key)
            # 利用可能なカテゴリリストを取得
            from presentation.const import CATEGORIES  # 遅延インポート

            # CATEGORIES はリストとして定義されているため keys() ではなくイテレートする
            available_categories = ", ".join([f"'{cat}'" for cat in CATEGORIES])

            prompt = getPredictExpenseReportPrompt(text, available_categories)
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

    def apply_intent(self, intent: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """インテントを受けてサーバ側で行動を起こす（DB取得→フォームデータ返却）

        対応するインテント:
        - fetch_previous: 過去の申請データを取得（days_ago パラメータで日数指定）
        - fetch_by_category: カテゴリで申請をフィルタリング
        - set_amount: 金額を設定

        Returns:
            form_data dict (possibly empty) to apply to the form.
        """
        intent_name = intent.get("intent")
        data = {}

        # fetch_previous: 指定日数前の申請データを取得
        if intent_name == "fetch_previous":
            days_ago = intent.get("days_ago", 1)
            data = self.fetch_recent_submission_by_days(user_id, days_ago=days_ago)

            # フィルタリング（カテゴリ指定がある場合）
            if data and "category" in intent:
                target_category = intent.get("category")
                # data に複数のカテゴリがある場合、指定カテゴリのみを抽出
                if isinstance(data, dict):
                    filtered = {
                        k: v
                        for k, v in data.items()
                        if self._matches_category(k, target_category)
                    }
                    data = filtered if filtered else data

            # 金額を上書き（金額指定がある場合）
            if data and "amount" in intent:
                data["amount"] = intent.get("amount")

            logger.info(
                "Applied fetch_previous intent with days_ago=%d, result=%s",
                days_ago,
                data,
            )
            # return data or {}

        # fetch_by_category: カテゴリで最近の申請をフィルタリング
        elif intent_name == "fetch_previous_by_category":
            category = intent.get("category")
            data = self.fetch_recent_submission(user_id, limit=5)
            if data and category:
                filtered = {
                    k: v for k, v in data.items() if self._matches_category(k, category)
                }
                data = filtered if filtered else data
            logger.info(
                "Applied fetch_by_category intent with category=%s, result=%s",
                category,
                data,
            )
            return data or {}

        elif intent_name == "fetch_previous_by_destination":
            destination = intent.get("destination")
            days_ago = intent.get("days_ago")
            data = self.fetch_recent_submission_by_days(user_id, days_ago=days_ago)
            if data and destination:
                filtered = {
                    k: v
                    for k, v in data.items()
                    if isinstance(v, str) and re.search(destination, v, re.IGNORECASE)
                }
                data = filtered if filtered else data
            logger.info(
                "Applied fetch_by_destination intent with destination=%s, days_ago=%d, result=%s",
                destination,
                days_ago,
                data,
            )
            return data or {}

        # set_amount: 金額のみを設定
        elif intent_name == "set_amount":
            amount = intent.get("amount")
            logger.info("Applying set_amount intent with amount=%s", amount)
            return {"amount": amount}

        # unknown / fallback
        else:
            logger.info("Unknown intent, returning empty dict")
            return {}

        if data and "date" in data:
            del data["user"]
            del data["date"]  # 日付は現在日付を使う想定
            del data["uploaded_file"]

        return data

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
