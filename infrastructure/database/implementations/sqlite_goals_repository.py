from dataclasses import asdict

import aiosqlite

from app.core.logs_config.logger_wrappers import repository_logger
from domain.entities.goal import Goal
from domain.repositories.base_goals_repository import BaseGoalsRepository


class SqliteGoalsRepository(BaseGoalsRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
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
    async def init_db(self) -> None:
        db = await self._get_db()
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS goals(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                user_id INTEGER NOT NULL,
                order_number INTEGER NOT NULL,
                
                text TEXT,
                target FLOAT DEFAULT 0,
                curr_bill FLOAT DEFAULT 0,
                
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                
                UNIQUE(user_id, order_number)
            );
        """)

        await db.execute(
            "CREATE INDEX IF NOT EXISTS index_goals_user_orders ON goals(user_id, order_number);"
        )

        await db.commit()

    @repository_logger
    async def get_order_number_for_user(self, user_id: int) -> int:
        db = await self._get_db()
        cursor = await db.execute(
            "SELECT MAX(order_number) AS last_num FROM goals WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row["last_num"] if row and row["last_num"] is not None else 0

    @repository_logger
    async def save_goal(self, goal: Goal) -> None:
        db = await self._get_db()
        await db.execute(
            "INSERT INTO goals(user_id, order_number, target, curr_bill, text, created_at) \
            VALUES(:user_id, :order_number, :target, :curr_bill, :text, :created_at)",
            asdict(goal),
        )
        await db.commit()

    @repository_logger
    async def get_all_user_goals(self, user_id: int) -> list[Goal]:
        db = await self._get_db()
        cur = await db.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
        data = await cur.fetchall()
        return [Goal(**row) for row in data]

    @repository_logger
    async def get_goal_attrs(self, user_id: int, order_number: int) -> Goal:
        db = await self._get_db()
        cursor = await db.execute(
            "SELECT * FROM goals WHERE user_id = ? AND order_number = ?",
            (user_id, order_number),
        )
        row = await cursor.fetchone()
        if row:
            return Goal(**dict(row))
        return None

    @repository_logger
    async def update_goal(self, goal: Goal) -> None:
        db = await self._get_db()
        await db.execute(
            "UPDATE goals SET curr_bill = ? WHERE user_id = ? AND order_number = ?",
            (goal.curr_bill, goal.user_id, goal.order_number),
        )
        await db.commit()

    @repository_logger
    async def delete_goal(self, goal: Goal) -> None:
        db = await self._get_db()
        await db.execute(
            "DELETE FROM goals WHERE user_id = ? AND order_number = ?",
            (goal.user_id, goal.order_number),
        )

        await db.commit()

    @repository_logger
    async def change_goal_text(
        self, user_id: int, order_number: int, new_text: str
    ) -> None:
        db = await self._get_db()
        await db.execute(
            "UPDATE goals SET text = ? WHERE user_id = ? AND order_number = ?",
            (new_text, user_id, order_number),
        )
        await db.commit()

    @repository_logger
    async def get_user_goals_count(self, user_id: int) -> int:
        db = await self._get_db()
        cursor = await db.execute(
            "SELECT COUNT(order_number) FROM goals WHERE user_id = ?", (user_id,)
        )
        data = await cursor.fetchone()
        return data[0] if data[0] else 0

    @repository_logger
    async def get_users(self) -> list[int]:
        db = await self._get_db()
        cursor = await db.execute("SELECT user_id FROM goals")
        return [row[0] for row in await cursor.fetchall()]
