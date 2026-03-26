from aiogram.types import Message

from domain.entities.goal import Goal
from repository.base_goals_repository import BaseGoalsRepository


class ChangeGoalDescUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: Message, goal_id: int) -> None:
        if not message.text or not message.from_user:
            return

        user_id = message.from_user.id

        await self.goal_repository.change_goal_text(user_id, goal_id, message.text)
