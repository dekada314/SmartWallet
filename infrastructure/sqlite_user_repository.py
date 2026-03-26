from datetime import datetime

import aiosqlite

from domain.entities.user import User
from repository.base_user_repository import BaseUserRepository


class SQLiteUserRepository(BaseUserRepository):
    def __init__(self, user_db_path: str):
        self.db_path = user_db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users(
                        user_id INTEGER PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        balance REAL NOT NULL,
                        created_at DATE,
                        last_action DATE
                         
                ) 
            """)

            await db.commit()

    async def save_user(self, user: User) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO users(user_id, user_name, balance, created_at, last_action) VALUES (?, ?, ?, ?, ?)",
                (
                    user.user_id,
                    user.user_name,
                    user.balance,
                    user.created_at,
                    user.last_action,
                ),
            )

            await db.commit()

    async def delete_user_by_user_id(self, user_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

            await db.commit()

    async def get_user_by_user_id(self, user_id: int) -> User | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )

            row = await cursor.fetchone()
            if row:
                return User(
                    user_id=row["user_id"],
                    user_name=row["user_name"],
                    balance=row["balance"],
                    created_at=row["created_at"],
                    last_action=row["last_action"],
                )
            return None

    async def update_last_action(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET last_action = ? WHERE user_id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
            )

            await db.commit()

    async def update_balance(self, user_id: int, delta: int | float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (delta, user_id),
            )

            await db.commit()
