from aiogram.types import CallbackQuery, Message

from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.del_goal_request import DelGoalRequest
from domain.entities.goal import Goal
from domain.repositories.base_goals_repository import BaseGoalsRepository


class DeleteGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    @use_case_logger
    async def execute(self, dto: DelGoalRequest) -> None:
        if not dto.user_id or not dto.user_goal_id:
            return

        goal: Goal = await self.goal_repository.get_goal_attrs(
            dto.user_id, dto.user_goal_id
        )

        await self.goal_repository.delete_goal(goal)
