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
                    transaction_id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    created_ad DATE,
                    description TEXT
            ) 
        """)
        
        self.conn.commit()
    
    
    async def save_transaction(self, transaction: Transaction) -> None:
        self.cursor.execute(
            "INSERT OR REPLACE INTO transactions(?, ?, ?)",
            (transaction.transaction_id, transaction.category, transaction.balance)
        )
        
        self.conn.commit()
        
    async def delete_transaction_by_id(self, transaction_id: int) -> None:
        self.cursor.execute(
            "DELETE FROM transactions WHERE transaction_id = ?",(transaction_id,)
            )
        
        self.conn.commit()
        
    async def get_transaction_by_transaction_id(self, transaction_id: int) -> Transaction | None:
        self.cursor.execute(
            "SELECT * FROM transactions WHERE transaction_id = ?",
            (transaction_id)
        )
        row = self.cursor.fetchone()
        if row:
            return Transaction(transaction_id=row['transaction_id'], transaction_name=row['transaction_name'], balance=row['balance'])
        self.conn.commit()
        return None