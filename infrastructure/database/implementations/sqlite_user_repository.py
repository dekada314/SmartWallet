from dataclasses import asdict
from datetime import datetime

import aiosqlite

from app.core.logs_config.logger_wrappers import repository_logger
from domain.entities.user import User
from domain.repositories.base_user_repository import BaseUserRepository


class SQLiteUserRepository(BaseUserRepository):
    def __init__(self, user_db_path: str):
        self.db_path = user_db_path
        self._db: aiosqlite.Connection | None = None

    async def _get_db(self):
        if self._db is None:
            self._db = await aiosqlite.connect(self.db_path)
            self._db.row_factory = aiosqlite.Row

            await self._db.execute("PRAGMA foreign_keys=ON")
            await self._db.execute("PRAGMA journal_mode=WAL")
            await self._db.execute("PRAGMA synchronous=NORMAL")
            await self._db.execute("PRAGMA cache_size=-64000")
        return self._db

    @repository_logger
    async def init_db(self):
        db = await self._get_db()
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    balance REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_action DATETIME DEFAULT CURRENT_TIMESTAMP
                        
            ) 
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS index_user_id ON users(user_id)")

        await db.commit()

    @repository_logger
    async def save_user(self, user: User) -> None:
        db = await self._get_db()
        await db.execute(
            "INSERT OR REPLACE INTO users(user_id, user_name, balance, created_at, last_action) \
            VALUES (:user_id, :user_name, :balance, :created_at, :last_action)",
            asdict(user)
        )

        await db.commit()

    @repository_logger
    async def delete_user_by_user_id(self, user_id: int) -> None:
        db = await self._get_db()
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

        await db.commit()

    @repository_logger
    async def get_user_by_user_id(self, user_id: int) -> User | None:
        db = await self._get_db()
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

        row = await cursor.fetchone()
        if row:
            return User(**row)
        return None

    @repository_logger
    async def update_last_action(self, user_id: int):
        db = await self._get_db()
        await db.execute(
            "UPDATE users SET last_action = ? WHERE user_id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id),
        )

        await db.commit()

    @repository_logger
    async def update_balance(self, user_id: int, delta: int | float) -> None:
        db = await self._get_db()
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (delta, user_id),
        )

        await db.commit()
