import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class ApprovalRepository:
    """申請データをSQLiteで管理するリポジトリ"""

    def __init__(self, db_path: str = "data/approvals.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """DBテーブルを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 申請テーブル
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                approved_by TEXT,
                approved_at TEXT,
                rejection_reason TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    def add_submission(self, user_id: str, category: str, data: Dict[str, Any]) -> int:
        """申請を追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        submitted_at = datetime.now().isoformat()
        data_json = json.dumps(data, ensure_ascii=False)

        cursor.execute(
            """
            INSERT INTO submissions (user_id, category, submitted_at, data, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (user_id, category, submitted_at, data_json),
        )

        conn.commit()
        submission_id = cursor.lastrowid
        conn.close()

        return submission_id

    def get_pending_submissions(self) -> List[Dict[str, Any]]:
        """未承認の申請一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, category, submitted_at, data, status
            FROM submissions
            WHERE status = 'pending'
            ORDER BY submitted_at DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "user_id": row[1],
                    "category": row[2],
                    "submitted_at": row[3],
                    "data": json.loads(row[4]),
                    "status": row[5],
                }
            )

        return result

    def get_submission_by_id(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """IDで申請を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, category, submitted_at, data, status, approved_by, approved_at, rejection_reason
            FROM submissions
            WHERE id = ?
            """,
            (submission_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "user_id": row[1],
            "category": row[2],
            "submitted_at": row[3],
            "data": json.loads(row[4]),
            "status": row[5],
            "approved_by": row[6],
            "approved_at": row[7],
            "rejection_reason": row[8],
        }

    def approve_submission(self, submission_id: int, approved_by: str) -> bool:
        """申請を承認"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        approved_at = datetime.now().isoformat()

        cursor.execute(
            """
            UPDATE submissions
            SET status = 'approved', approved_by = ?, approved_at = ?
            WHERE id = ?
            """,
            (approved_by, approved_at, submission_id),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def reject_submission(self, submission_id: int, rejection_reason: str) -> bool:
        """申請を却下"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE submissions
            SET status = 'rejected', rejection_reason = ?
            WHERE id = ?
            """,
            (rejection_reason, submission_id),
        )

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        return success

    def get_all_submissions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """全申請を取得（オプションでステータスでフィルタ）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute(
                """
                SELECT id, user_id, category, submitted_at, data, status
                FROM submissions
                WHERE status = ?
                ORDER BY submitted_at DESC
                """,
                (status,),
            )
        else:
            cursor.execute(
                """
                SELECT id, user_id, category, submitted_at, data, status
                FROM submissions
                ORDER BY submitted_at DESC
                """
            )

        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "user_id": row[1],
                    "category": row[2],
                    "submitted_at": row[3],
                    "data": json.loads(row[4]),
                    "status": row[5],
                }
            )

        return result

    def get_top_rejection_reasons(self, limit: int = 3) -> List[Dict[str, Any]]:
        """却下理由のTOP Nを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT rejection_reason, COUNT(*) as count
            FROM submissions
            WHERE status = 'rejected' AND rejection_reason IS NOT NULL AND rejection_reason != ''
            GROUP BY rejection_reason
            ORDER BY count DESC
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [{"reason": row[0], "count": row[1]} for row in rows]

    def get_top_rejection_reasons_by_user(
        self, user_id: str, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """ユーザーごとの却下理由のTOP Nを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT rejection_reason, COUNT(*) as count
            FROM submissions
            WHERE user_id = ? AND status = 'rejected' AND rejection_reason IS NOT NULL AND rejection_reason != ''
            GROUP BY rejection_reason
            ORDER BY count DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [{"reason": row[0], "count": row[1]} for row in rows]
