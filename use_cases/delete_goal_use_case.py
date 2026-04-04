from aiogram.types import CallbackQuery, Message

from domain.entities.goal import Goal
from repository.base_goals_repository import BaseGoalsRepository


class DeleteGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: CallbackQuery, goal_id: int) -> None:
        if not message.from_user.id or not goal_id:
            return
        
        goal: Goal = await self.goal_repository.get_goal_attrs(
            message.from_user.id, goal_id
        )

        await self.goal_repository.delete_goal(goal)
