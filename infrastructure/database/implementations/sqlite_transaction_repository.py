from dataclasses import astuple
from datetime import datetime

import aiosqlite

from domain.entities.transaction import Transaction
from domain.repositories.base_transaction_repository import BaseTransactionRepository


class SQLiteTransactionRepository(BaseTransactionRepository):
    def __init__(self, transaction_db_path: str):
        self.db_path = transaction_db_path

    async def init_db(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_transaction_id INTEGER NOT NULL,
                    category TEXT,
                    amount REAL NOT NULL,
                    source_text TEXT,
                    transaction_type TEXT NOT NULL,
                    created_at DATE
            ) 
        """)

            await db.commit()

    async def get_last_id(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT MAX(user_transaction_id) AS last_id FROM transactions WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row[0] else 0

    async def save_transaction(self, transaction: Transaction) -> None:
        values = astuple(transaction)[:-2] + (
            transaction.transaction_type.value,
            transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO transactions(user_id, user_transaction_id, category, amount, source_text, transaction_type,  created_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
                values,
            )
            await db.commit()

    async def delete_by_transaction_id(self, user_id, user_transaction_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM transactions WHERE user_id = ? AND user_transaction_id = ?",
                (user_id, user_transaction_id),
            )

            await db.commit()

    async def get_transaction_by_transaction_id(
        self, user_id, user_transaction_id: int
    ) -> Transaction | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transactions WHERE user_id = ? AND user_transaction_id = ?",
                (user_id, user_transaction_id),
            )
            data = await cursor.fetchone()
            if data:
                data = dict(data)
                data.pop("id", None)
                return Transaction(**data)
        return None

    async def get_user_transactions_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(user_transaction_id) FROM transactions WHERE user_id = ?",
                (user_id,),
            )
            data = await cursor.fetchone()
            return data[0] if data[0] else 0

    async def get_transactions_by_period(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transactions WHERE user_id = ? AND created_at BETWEEN ? AND ?",
                (user_id, start_date, end_date),
            )
            transactions = []

            async for row in cursor:
                row = dict(row)
                row.pop("id", None)
                transactions.append(Transaction(**row))
            return transactions
