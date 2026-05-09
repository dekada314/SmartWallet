from dataclasses import astuple
from datetime import datetime

import aiosqlite

from app.core.logs_config.logger_wrappers import repository_logger
from domain.entities.transaction import Transaction
from domain.repositories.base_transaction_repository import BaseTransactionRepository


class SQLiteTransactionRepository(BaseTransactionRepository):
    def __init__(self, transaction_db_path: str):
        self.db_path = transaction_db_path
        self._db: aiosqlite.Connection | None = None

    async def _get_db(self):
        if self._db is None:
            self._db = aiosqlite.connect(self.db_path)
            self._db.row_factory = aiosqlite.Row

            await self._db.execute("PRAGMA foreign_keys=ON")
            await self._db.execute("PRAGMA journal_mode=WAL")
            await self._db.execute("PRAGMA synchronous=NORMAL")
            await self._db.execute("PRAGMA cache_size=-64000")

        return self._db

    @repository_logger
    async def init_db(self) -> None:
        db = await self._get_db()
        await db.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number INTEGER NOT NULL,
                
                category TEXT,
                source_text TEXT,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY(user_id) REFERENCES users(user_id) DELETE CASCADE,
        );
    """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS index_user_order_id(user_id, order_number);"
        )

        await db.commit()

    @repository_logger
    async def get_last_id(self, user_id: int) -> int:
        db = await self._get_db()
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT MAX(order_number) AS last_id FROM transactions WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row[0] else 0

    @repository_logger
    async def save_transaction(self, transaction: Transaction) -> None:
        values = astuple(transaction)[:-2] + (
            transaction.transaction_type.value,
            transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        db = await self._get_db()
        await db.execute(
            "INSERT OR REPLACE INTO transactions(user_id, order_number, category, amount, source_text, transaction_type, created_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
            values,
        )
        await db.commit()

    @repository_logger
    async def delete_by_transaction_id(self, user_id, order_number: int) -> None:
        db = await self._get_db()
        await db.execute(
            "DELETE FROM transactions WHERE user_id = ? AND order_number = ?",
            (user_id, order_number),
        )

        await db.commit()

    @repository_logger
    async def get_transaction_by_transaction_id(
        self, user_id, order_number: int
    ) -> Transaction | None:
        db = await self._get_db()
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND order_number = ?",
            (user_id, order_number),
        )
        data = await cursor.fetchone()
        if data:
            return Transaction(**dict(data))
        return None

    @repository_logger
    async def get_user_transactions_count(self, user_id: int) -> int:
        db = await self._get_db()
        cursor = await db.execute(
            "SELECT COUNT(order_number) FROM transactions WHERE user_id = ?",
            (user_id,),
        )
        data = await cursor.fetchone()
        return data[0] if data[0] else 0

    @repository_logger
    async def get_transactions_by_period(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> list[Transaction]:
        db = await self._get_db()
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM transactions WHERE user_id = ? AND created_at BETWEEN ? AND ?",
            (user_id, start_date, end_date),
        )
        transactions = []

        async for row in cursor:
            transactions.append(Transaction(**dict(row)))
        return transactions

    # @repository_logger
    # async def get_rule_for_situation(self, condition: str) -> int:
    #     db = await self._get_db()
    #     cursor = await db.execute(
    #         f"SELECT COUNT(order_number) FROM transactions AS tr JOIN users AS us ON (tr.user_id = us.user_id) {condition}",
    #     )
    #     data = await cursor.fetchone()
    #     return data[0] if data[0] else 0
