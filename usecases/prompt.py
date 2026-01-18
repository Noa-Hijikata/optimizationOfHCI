def getPredictExpenseReportPrompt(text: str, available_categories: str) -> str:
    return f"""
            ユーザーの入力テキストを解析し、経費申請に関する意図 (intent) と、関連するパラメータをJSON形式で抽出してください。
            利用可能なインテント:
            - 'fetch_previous': 過去の申請データを取得したい場合。days_ago (int): 何日前か。例: '昨日'->1, '先週'->7, '先月'->30。
            - 'fetch_previous_by_category': 特定のカテゴリの申請データを取得したい場合。category (str): 以下のいずれかのカテゴリ名: {available_categories}。
            - 'fetch_previous_by_destination': 特定の目的地の申請データを取得したい場合。destination (str): 目的地はどこか。例: '東京', '大阪'。
            - 'set_amount': 金額を設定したい場合。amount (int): 金額。
            - 'unknown': 上記に該当しない場合。

            抽出するJSONの構造:
            {{"intent": "<intent_name>", "days_ago": <int>, "category": "<category_name>", "destination": "<destination_name>", "amount": <int>}}
            days_ago, category, destination, amount は関連するインテントの場合のみ含めてください。金額は数字のみ抽出してください。

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
            
            ユーザー: 「こんにちは」
            AI: {{"intent": "more_info_needed"}}

            ユーザー: 「{text}」
            AI:
            """
