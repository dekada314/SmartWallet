from app.core.logs_config.logger_wrappers import use_case_logger
from domain.repositories.base_goals_repository import BaseGoalsRepository


class ExceedingTheLimitUseCase:
    def __init__(self, goal_db: BaseGoalsRepository):
        self.goal_db = goal_db

    @use_case_logger
    async def execute(self, user_id: int) -> bool:
        count_of_goals = await self.goal_db.get_user_goals_count(user_id)
        if count_of_goals == 5:
            return False
        return True
