import pandas as pd, json, os, collections
import ast

from presentation.const import (
    EventType,
    CATEGORIES,
    BUTTONS_BASE,
    CAT_TRNSPORTS,
    CAT_BUSINESS_TRIP,
    SUGGESTS_TRNSPRTS,
    SUGGESTS_BUSINESS_TRIP,
    ORDER_TRNSPRTS,
    ORDER_BUSINESS_TRIP,
    TRANSPORTATION,
)

LOG_FILE = "data/logs.csv"
CONFIG_DIR = "personalized"


class Personalization:
    def __init__(self, config_dir=CONFIG_DIR):
        self.config_dir = config_dir

    def topn(self, lst, n=5):
        cnt = collections.Counter(lst)
        return [k for k, _ in cnt.most_common(n)]

    def parse_list_str_to_dict(self, s):
        """
        s: 例 -> "['{...}']" や "['{\"key\": \"val\"}']" や "{...}"
        戻り値: dict (パース失敗時は ValueError)
        """
        # まず ast.literal_eval で安全に評価
        try:
            outer = ast.literal_eval(s)
        except Exception:
            # ast でダメなら JSON として試す
            try:
                parsed = json.loads(s)
            except Exception as e:
                raise ValueError(f"cannot parse input: {e}")
            # JSON が dict なら返す、list なら最初の要素を扱う
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list) and parsed:
                if isinstance(parsed[0], dict):
                    return parsed[0]
                if isinstance(parsed[0], str):
                    try:
                        return json.loads(parsed[0])
                    except Exception as e:
                        raise ValueError(f"cannot parse inner JSON: {e}")
            raise ValueError("unexpected JSON structure")

        # ast で評価できた場合
        if isinstance(outer, dict):
            return outer
        if isinstance(outer, list) and outer:
            first = outer[0]
            if isinstance(first, dict):
                return first
            if isinstance(first, str):
                try:
                    return ast.literal_eval(first)
                except Exception:
                    try:
                        return json.loads(first)
                    except Exception as e:
                        raise ValueError(f"cannot parse inner element: {e}")
        raise ValueError("unexpected structure after ast parsing")

    def load_config(self, user_id):
        # ユーザーIDが指定されていない場合は即座に返す
        if not user_id or user_id.strip() == "":
            return None

        os.makedirs(self.config_dir, exist_ok=True)

        if not os.path.exists(LOG_FILE):
            return None
        logs = pd.read_csv(LOG_FILE, dtype=str)

        if logs is None or logs.empty:
            return None

        # 必要なカラムが無ければ中断
        if "user_id" not in logs.columns or "event" not in logs.columns:
            return None

        # --- ユーザーフィルタリング ---
        g = logs[logs["user_id"] == user_id]
        if g.empty:
            return None

        # --- カテゴリ追加ボタン頻度 (event='button' & category in CATEGORIES) ---
        cat_cnt = collections.Counter(
            [
                c
                for c in g[
                    (g["event"] == "button")
                    & g["category"].notna()
                    & g["category"].isin(CATEGORIES)
                ]["category"]
                if c
            ]
        )
        category_order = [c for c, _ in cat_cnt.most_common()] + [
            c for c in CATEGORIES if c not in cat_cnt
        ]

        trnsprts_config = self.load_trnsprts_config(
            g[
                (g["category"] == CAT_TRNSPORTS)
                & (g["event"] == EventType.FORMSUBMIT.value)
            ]
        )
        bussinessTrip_config = self.load_bussinessTrip_config(
            g[
                (g["category"] == CAT_BUSINESS_TRIP)
                & (g["event"] == EventType.FORMSUBMIT.value)
            ]
        )

        cfg = {
            "category_order": category_order,
            "trnsprts_config": trnsprts_config,
            "bussinessTrip_config": bussinessTrip_config,
            "defaults": {},
        }

        return cfg

    def load_trnsprts_config(self, g):
        suggests = self.load_suggests_config(g, CAT_TRNSPORTS)
        order = self.load_order_config(g, CAT_TRNSPORTS)
        return {"suggests": suggests, "order": order}

    def load_bussinessTrip_config(self, g):
        suggests = self.load_suggests_config(g, CAT_BUSINESS_TRIP)
        order = self.load_order_config(g, CAT_BUSINESS_TRIP)
        return {"suggests": suggests, "order": order}

    def _extract_submission_dicts(self, series):
        """
        series: pandas Series（'value' 列）から、フォーム送信の辞書を取り出してリストで返す。
        value が既に dict の場合はそれを使い、文字列の場合は parse_list_str_to_dict で解析する。
        解析失敗・空値はスキップする。
        """
        dicts = []
        for v in series.tolist():
            if v is None:
                continue
            # pandas の欠損値チェック
            try:
                if pd.isna(v):
                    continue
            except Exception:
                pass
            # 既に dict ならそのまま
            if isinstance(v, dict):
                dicts.append(v)
                continue
            # 文字列ならトリムして空ならスキップ
            if isinstance(v, str):
                s = v.strip()
                if not s:
                    continue
                # try parse
                try:
                    d = self.parse_list_str_to_dict(s)
                except Exception:
                    # 最終手段として JSON.loads を試す（例: '{"k":"v"}'）
                    try:
                        parsed = json.loads(s)
                        if isinstance(parsed, dict):
                            dicts.append(parsed)
                    except Exception:
                        # パース不能ならスキップ
                        continue
                else:
                    if isinstance(d, dict):
                        dicts.append(d)
        return dicts

    def load_suggests_config(self, g, category):
        suggests = {}
        if category == CAT_TRNSPORTS:
            fields = SUGGESTS_TRNSPRTS
        elif category == CAT_BUSINESS_TRIP:
            fields = SUGGESTS_BUSINESS_TRIP
        else:
            return suggests

        if g.empty:
            return suggests

        submissions = self._extract_submission_dicts(
            g[(g["event"] == EventType.FORMSUBMIT.value)]["value"]
        )
        if not submissions:
            return suggests

        for field in fields:
            entries = [
                d.get(field)
                for d in submissions
                if field in d and d.get(field) is not None
            ]
            # normalize strings and drop empty / whitespace / "nan"
            clean = [
                str(e).strip()
                for e in entries
                if e is not None and str(e).strip() and str(e).strip().lower() != "nan"
            ]
            cnt = collections.Counter(clean)
            suggests[field] = [k for k, _ in cnt.most_common(5)]

        return suggests

    def load_order_config(self, g, category):
        orderlists = {}
        if category == CAT_TRNSPORTS:
            fields = ORDER_TRNSPRTS
        elif category == CAT_BUSINESS_TRIP:
            fields = ORDER_BUSINESS_TRIP
        else:
            return orderlists

        if g.empty:
            return orderlists

        submissions = self._extract_submission_dicts(
            g[(g["event"] == EventType.FORMSUBMIT.value)]["value"]
        )
        if not submissions:
            return orderlists

        for field in fields:
            entries = [
                d.get(field)
                for d in submissions
                if field in d and d.get(field) is not None
            ]
            clean = [
                str(e).strip()
                for e in entries
                if e is not None and str(e).strip() and str(e).strip().lower() != "nan"
            ]
            v_cnt = collections.Counter(clean)
            # 優先順（出現順）＋既知の輸送手段補完
            order = [c for c, _ in v_cnt.most_common()] + [
                c for c in TRANSPORTATION if c not in v_cnt
            ]
            orderlists[field] = order

        return orderlists
