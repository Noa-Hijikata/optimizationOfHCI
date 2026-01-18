from datetime import datetime, date


def safe_strftime(val, fmt):
    if isinstance(val, (datetime, date)):
        return val.strftime(fmt)
    if isinstance(val, str):
        # ISO 形式の文字列なら fromisoformat で試す
        try:
            return datetime.fromisoformat(val).strftime(fmt)
        except Exception:
            pass
        # 数値（timestamp の文字列）なら timestamp として試す
        try:
            ts = float(val)
            return datetime.fromtimestamp(ts).strftime(fmt)
        except Exception:
            pass
        # パースできなければそのまま返す（表示のみの目的）
        return val
    # その他（None 等）
    try:
        return str(val)
    except Exception:
        return "<unprintable>"


import json
import re


def parse_ai_response(response_text: str) -> dict:
    """
    AIの応答テキストからJSON部分を抽出して辞書に変換する
    """
    try:
        # 1. 完全に整形されたJSONの場合
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    try:
        # 2. Markdownコードブロック ```json ... ``` がある場合や、余計なテキストがある場合
        # JSONらしい部分（最初の '{' から 最後の '}' まで）を正規表現で抽出
        match = re.search(r"(\{.*\})", response_text, re.DOTALL)
        if match:
            json_str = match.group(1)
            # 文字列内の改行などをクリアにする必要があればここで処理
            return json.loads(json_str)
    except Exception as e:
        print(f"JSON extract error: {e}")

    # パース失敗時はエラー情報を含む辞書を返す（または空辞書）
    return {"intent": "unknown", "_error": "Failed to parse JSON"}
