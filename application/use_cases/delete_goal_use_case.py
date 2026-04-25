from aiogram.types import CallbackQuery, Message
from repository.base_goals_repository import BaseGoalsRepository

from app.dto.requests.del_goal_request import DelGoalRequest
from domain.entities.goal import Goal


class DeleteGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, dto: DelGoalRequest) -> None:
        if not dto.user_id or not dto.user_goal_id:
            return

        goal: Goal = await self.goal_repository.get_goal_attrs(
            dto.user_id, dto.user_goal_id
        )

        await self.goal_repository.delete_goal(goal)
