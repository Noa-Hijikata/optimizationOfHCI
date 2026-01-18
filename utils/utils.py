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
