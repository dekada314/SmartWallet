from app.core.logs_config.logger_wrappers import use_case_logger
from domain.entities.goal import Goal
from domain.repositories.base_goals_repository import BaseGoalsRepository


class DisplayUserGoals:
    def __init__(self, goal_db: BaseGoalsRepository):
        self.goad_db = goal_db

    @use_case_logger
    async def execute(self, user_id):
        goals: list[Goal] = await self.goad_db.get_all_user_goals(user_id)
        return goals
