import sqlite3

from domain.entities.transaction import Transaction
from repository.base_transaction_repository import BaseTransactionRepository


class SQLiteTransactionRepository(BaseTransactionRepository):
    def __init__(self, transaction_db_path: str):
        self.conn = sqlite3.connect(transaction_db_path)
        self.conn.row_factory = sqlite3.Row

        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    transaction_id TEXT,
                    category TEXT NOT NULL,
                    amount REAL,
                    created_at DATE
            ) 
        """)

        self.conn.commit()

    async def save_transaction(self, user_id: int, transaction: Transaction) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO transactions(user_id, transaction_id, category, amount, created_at) VALUES(?, ?, ?, ?, ?)",
            (user_id, transaction.transaction_id, transaction.category, transaction.amount, transaction.created_at),
        )

        self.conn.commit()

    async def delete_by_transaction_id(self, transaction_id: int) -> None:
        self.conn.execute(
            "DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,)
        )

        self.conn.commit()

    async def get_transaction_by_transaction_id(
        self, transaction_id: int
    ) -> Transaction | None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id)
        )
        row = cursor.fetchone()
        if row:
            return Transaction(
                transaction_id=row["transaction_id"],
                amount=row["amount"],
                category=row["category"],
                created_at=row["created_at"]
            )
        self.conn.commit()
        return None
