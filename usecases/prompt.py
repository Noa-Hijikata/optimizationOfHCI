import json


def getPredictExpenseReportPrompt(
    text: str, available_categories: str, history: list = None
) -> str:
    history_context = ""
    if history:
        history_context = "過去の対話履歴:\n"
        for chat in history:
            role = "ユーザー" if chat["role"] == "user" else "AI"
            history_context += f"{role}: {chat['message']}\n"
        history_context += "\n"
    return f"""
            {history_context}
            最新のユーザー入力テキスト「{text}」を解析し、経費申請に関する意図 (intent) と、関連するパラメータをJSON形式で抽出してください。
            過去の対話履歴がある場合は、その文脈（目的地や金額など）も考慮して推測してください。
            利用可能なカテゴリ一覧: {available_categories}
            利用可能なインテント:
            - 'fetch_previous': 過去の申請データを取得したい場合。
            - 'fetch_previous_by_category': 特定のカテゴリの申請データを取得したい場合。
            - 'fetch_previous_by_destination': 特定の目的地の申請データを取得したい場合。
            - 'suggest_new': 新しい申請内容を提案してほしい場合（ユーザーが「〜へ行った」「〜の申請をしたい」と言った時）。
            - 'set_amount': 金額を設定したい場合。

            金額推測のルール:
            - 'suggest_new' の際、departure (出発地) と arrival (到着地) が判明していて金額が不明な場合、一般的な公共交通機関や高速料金を考慮したもっともらしい金額（円単位）を推測して amount に含めてください。
            - 不明な項目（car_name, purpose など）は無理に埋めず空のままにしてください。

            抽出するJSONの構造（suggest_newの場合）:
            {{"intent": "suggest_new", "category": "交通費精算"|"出張精算", "data": {{"destination": "...", "departure": "...", "arrival": "...", "amount": <int>, "purpose": "...", "transportation": "..."}}}}

            例:
            ユーザー: 「昨日と同じ内容で」
            AI: {{"intent": "fetch_previous", "days_ago": 1}}

            ユーザー: 「交通費を5000円で申請したい」
            AI: {{"intent": "set_amount", "amount": 5000, "category": "transportation"}}

            ユーザー: 「二日前の交通費を教えて」
            AI: {{"intent": "fetch_previous_by_category", "category": "transportation", "days_ago": 2}}
            
            ユーザー: 「先週の北海道の出張費を教えて」
            AI: {{"intent": "fetch_previous_by_destination", "category": "bussinessTrip", "destination": "北海道", "days_ago": 7}}

            ユーザー: 「今週のランチ代」
            AI: {{"intent": "fetch_previous_by_category", "category": "meal", "days_ago": 7}}
            
            ユーザー: 「明日は大阪へ出張します。新幹線で行きます。」
            AI: {{"intent": "suggest_new", "category": "出張精算", "data": {{"destination": "大阪", "departure": "東京", "arrival": "新大阪", "amount": 14500, "purpose": "出張", "transportation": "公共交通機関"}}}}
            
            ユーザー: 「こんにちは」
            AI: {{"intent": "more_info_needed"}}

            ユーザー: 「{text}」
            AI:
            """


def getRefinementPrompt(
    user_input: str, history: list, status: str, candidates: list = None
) -> str:
    history_context = ""
    if history:
        history_context = "対話履歴:\n"
        for chat in history:
            role = "ユーザー" if chat["role"] == "user" else "AI"
            history_context += f"{role}: {chat['message']}\n"
        history_context += "\n"

    status_msg = ""
    if status == "multiple":
        # 候補を簡潔に表示するための整形
        simplified_candidates = []
        for c in candidates:
            simplified = {
                k: v
                for k, v in c.items()
                if k in ["date", "destination", "amount", "purpose", "transportation"]
            }
            simplified_candidates.append(simplified)

        status_msg = f"システム検索の結果、以下の複数の候補が見つかりました:\n{json.dumps(simplified_candidates, ensure_ascii=False, indent=2)}\n\nこれらを元に、ユーザーにどれが正しいか尋ねるか、特定の情報を追加で求めるメッセージを生成してください。"
    elif status == "not_found":
        status_msg = "システム検索の結果、条件に合う申請が見つかりませんでした。ユーザーに、他の情報（日付、目的地、金額など）を教えてもらうよう促すメッセージを生成してください。"

    return f"""
            {history_context}
            最新のユーザー入力: 「{user_input}」
            
            {status_msg}
            
            AIとして、ユーザーに親切に問いかけてください。自然な日本語で回答してください。
            AI:
            """
