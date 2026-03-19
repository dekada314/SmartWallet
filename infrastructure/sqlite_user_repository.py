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
                        balance REAL NOT NULL
                ) 
            """)

            await db.commit()

    async def save_user(self, user: User) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO users(user_id, user_name, balance) VALUES (?, ?, ?)",
                (user.user_id, user.user_name, user.balance),
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
                )
            return None
