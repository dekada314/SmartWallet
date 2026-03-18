import sqlite3

from domain.entities.user import User
from repository.base_user_repository import BaseUserRepository


class SQLiteUserRepository(BaseUserRepository):
    def __init__(self, user_db_path: str):
        self.conn = sqlite3.connect(user_db_path)
        self.conn.row_factory = sqlite3.Row

        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    balance REAL NOT NULL
            ) 
        """)

        self.conn.commit()

    async def save_user(self, user: User) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO users(user_id, user_name, balance) VALUES (?, ?, ?)",
            (user.user_id, user.user_name, user.balance),
        )

        self.conn.commit()

    async def delete_user_by_user_id(self, user_id: int) -> None:
        self.conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

        self.conn.commit()

    async def get_user_by_user_id(self, user_id: int) -> User | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

        row = cursor.fetchone()
        if row:
            return User(
                user_id=row["user_id"],
                user_name=row["user_name"],
                balance=row["balance"],
            )
        self.conn.commit()
        return None
