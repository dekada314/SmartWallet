import aiosqlite

from repository.base_goals_repository import BaseGoalsRepository


class SqliteGoalsRepository(BaseGoalsRepository):
    def __init__(self, goals_db_path: str):
        self.db_path = goals_db_path

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS goals(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    text TEXT
                )
            """)

            await db.commit()
            
    async def save_goal(self, user_id: int, text: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO goals(user_id, text) VALUES(?, ?)",
                (user_id, text)
            )
            await db.commit()
            
    async def get_all_user_goals(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
            data = await cur.fetchall()
            return [row["text"] for row in data]
