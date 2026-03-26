from aiogram.types import Message

from domain.entities.goal import Goal
from repository.base_goals_repository import BaseGoalsRepository


class DeleteGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: Message, goal_id: int) -> None:
        if not message.text or not message.from_user.id:
            return

        await self.goal_repository.delete_goal(message.from_user.id, goal_id)
