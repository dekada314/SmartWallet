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
                    user_goal_id INTEGER,
                    target FLOAT,
                    curr_bill FLOAT,
                    text TEXT
                )
            """)

            await db.commit()

    async def save_goal(self, user_id: int, target: float, curr_bill: float, text: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            cursor = await db.execute(
                "SELECT MAX(user_goal_id) AS last_num FROM goals WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            last_num = row["last_num"] if row["last_num"] else 0
            
            await db.execute(
                "INSERT INTO goals(user_id, user_goal_id, target, curr_bill, text) VALUES(?, ?, ?, ?, ?)",
                (user_id, last_num + 1, target, curr_bill, text),
            )
            await db.commit()
            
    async def get_all_user_goals(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
            data = await cur.fetchall()
            return [[row["text"], row["target"], row["curr_bill"]] for row in data]
        
    async def get_goal_attrs(self, user_id, goal_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM goals WHERE user_id = ? AND user_goal_id = ?",
                (user_id, goal_id)
            )
            return cursor.fetchone()
            

    async def update_goal(self, user_id: int, goal_id: str, new_curr_bill: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE goals SET curr_bill = curr_bill + ? WHERE user_id = ? AND user_goal_id = ?",
                (new_curr_bill, user_id, goal_id),
            )
            await db.commit()
            
    async def delete_goal(self, user_id, goal_id):
        pass
