import csv
import os
import json
from datetime import datetime
from domain.Entity.logEvent import LogEvent


class CSVLogRepository:

    def __init__(self, log_path):
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "user_id",
                        "mode",
                        "event",
                        "category",
                        "action",
                        "value",
                        "success",
                    ]
                )

    def save(self, log_event: LogEvent):
        with open(self.log_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    log_event.timestamp,
                    log_event.user_id,
                    log_event.mode,
                    log_event.event,
                    log_event.category,
                    log_event.action,
                    log_event.value,
                    log_event.success,
                ]
            )

    def get_recent_submissions(self, user_id: str, limit: int = 3) -> list:
        """
        直近のform_submitイベント（申請データ）を取得する。

        Args:
            user_id: ユーザーID
            limit: 取得件数（デフォルト3）

        Returns:
            申請データの辞書リストを時系列（新しい順）で返す。
            各要素は {timestamp, category, data} を含む。
        """
        submissions = []
        try:
            with open(self.log_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # form_submitイベントかつ該当ユーザーのみを抽出
                    if (
                        row.get("event") == "form_submit"
                        and row.get("user_id") == user_id
                        and row.get("success") == "True"
                    ):
                        try:
                            # value カラムを辞書にパース
                            value_str = row.get("value", "{}")
                            data = eval(
                                value_str
                            )  # セキュリティ考慮が必要な場合は json.loads を使用
                            submissions.append(
                                {
                                    "timestamp": float(row.get("timestamp", 0)),
                                    "datetime": datetime.fromtimestamp(
                                        float(row.get("timestamp", 0))
                                    ),
                                    "category": row.get("category", ""),
                                    "data": data,
                                }
                            )
                        except Exception:
                            # パースに失敗した場合はスキップ
                            continue
        except FileNotFoundError:
            pass

        # タイムスタンプ降順（新しい順）でソート
        submissions.sort(key=lambda x: x["timestamp"], reverse=True)

        return submissions[:limit]
