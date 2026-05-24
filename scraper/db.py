import sqlite3
import os
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "balances.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """テーブルを作成する（存在しなければ）"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            amount REAL NOT NULL,
            jpy_value REAL,
            fetched_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_balances_service_fetched
        ON balances (service, fetched_at)
    """)
    conn.commit()
    conn.close()


def save_balances(service: str, assets: list[dict]):
    """
    残高データを保存する。
    assets: [{"asset_name": "BTC", "amount": 0.5, "jpy_value": 5000000}, ...]
    """
    conn = get_connection()
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

    for asset in assets:
        conn.execute(
            """
            INSERT INTO balances (service, asset_name, amount, jpy_value, fetched_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                service,
                asset["asset_name"],
                asset["amount"],
                asset.get("jpy_value"),
                now,
            ),
        )

    conn.commit()
    conn.close()
    print(f"  [{service}] {len(assets)} assets saved")
