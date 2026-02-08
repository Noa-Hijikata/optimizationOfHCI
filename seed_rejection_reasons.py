import os
import sys
import sqlite3
import json
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from infrastructure.approvalRepository import ApprovalRepository


def setup_test_data():
    db_path = "data/approvals.db"
    # 既存のテストDBがあれば削除して作り直す（クリーンな状態にする場合）
    # if os.path.exists(db_path):
    #     os.remove(db_path)

    repo = ApprovalRepository(db_path=db_path)

    # テスト用の却下データを挿入
    reasons = [
        ("領収書の画像が不鮮明です", 5),
        ("金額が規定を超えています", 3),
        ("目的地の記入漏れがあります", 2),
        ("日付が間違っています", 1),
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for reason, count in reasons:
        for _ in range(count):
            submitted_at = datetime.now().isoformat()
            data = json.dumps({"test": "data"}, ensure_ascii=False)
            cursor.execute(
                """
                INSERT INTO submissions (user_id, category, submitted_at, data, status, rejection_reason)
                VALUES (?, ?, ?, ?, 'rejected', ?)
                """,
                ("test_user", "交通費精算", submitted_at, data, reason),
            )

    conn.commit()
    conn.close()

    print("Test data inserted successfully.")

    # TOP3が取得できるか確認
    top_reasons = repo.get_top_rejection_reasons(limit=3)
    print("Top 3 Rejection Reasons:")
    for i, item in enumerate(top_reasons):
        print(f"{i+1}. {item['reason']} ({item['count']} cases)")


if __name__ == "__main__":
    setup_test_data()
