import aiosqlite

from domain.entities.transaction import Transaction
from repository.base_transaction_repository import BaseTransactionRepository


class SQLiteTransactionRepository(BaseTransactionRepository):
    def __init__(self, transaction_db_path: str):
        self.db_path = transaction_db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    transaction_id TEXT,
                    category TEXT NOT NULL,
                    amount REAL,
                    created_at DATE
            ) 
        """)

            await db.commit()
            
    async def get_last_id(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT MAX(user_transaction_id) AS last_id FROM transactions WHERE user_id = ?",
                (user_id, )
            )
            row = await cursor.fetchone()[0]
            return row["last_id"] if row["last_id"] else 0
            

    async def save_transaction(self, transaction: Transaction) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO transactions(user_id, user_transaction_id, category, amount, created_at) VALUES(?, ?, ?, ?, ?)",
                (
                    transaction.user_id,
                    transaction.user_transaction_id,
                    transaction.category,
                    transaction.amount,
                    transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            await db.commit()

    async def delete_by_transaction_id(self, user_id, user_transaction_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM transactions WHERE user_id = ? AND user_transaction_id = ?", (user_id, user_transaction_id)
            )

            await db.commit()

    async def get_transaction_by_transaction_id(
        self, transaction_id: int
    ) -> Transaction | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id)
            )
            data = cursor.fetchone()
            if data:
                return Transaction(
                    transaction_id=data["transaction_id"],
                    amount=data["amount"],
                    category=data["category"],
                    created_at=data["created_at"],
                )
            self.conn.commit()
            return None

    async def get_user_transactions_count(self, user_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(user_transaction_id) FROM transactions WHERE user_id = ?",
                (user_id,),
            )
            data = await cursor.fetchone()
            return data[0] if data[0] else 0
