from repository.base_goals_repository import BaseGoalsRepository


class DisplayUserGoals:
    def __init__(self, goal_db: BaseGoalsRepository):
        self.goad_db = goal_db

    async def execute(self, user_id):
        goals = await self.goad_db.get_all_user_goals(user_id)
        return goals
