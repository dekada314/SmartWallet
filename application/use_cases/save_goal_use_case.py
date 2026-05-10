from aiogram.types import Message

from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.save_goal_request import SaveGoalRequest
from domain.entities.goal import Goal
from domain.entities.user import User
from domain.repositories.base_goals_repository import BaseGoalsRepository


class SaveGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    @use_case_logger
    async def execute(self, dto: SaveGoalRequest) -> User:
        user_id = dto.user_id
        last_user_goal_id = await self.goal_repository.get_order_number_for_user(
            user_id
        )
        try:
            new_goal = Goal(user_id, last_user_goal_id + 1, dto.amount, 0, dto.text)
            await self.goal_repository.save_goal(new_goal)
            return new_goal
        except Exception as e:
            raise
