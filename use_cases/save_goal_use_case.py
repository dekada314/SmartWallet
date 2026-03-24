from aiogram.types import Message

from domain.entities.goal import Goal
from domain.entities.user import User
from repository.base_goals_repository import BaseGoalsRepository


class SaveGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: Message, goal_text: str) -> User:
        user_id = message.from_user.id
        goal_id = await self.goal_repository.get_last_id(user_id) + 1
        try:
            target = float(message.text)

            new_goal = Goal(user_id, goal_id, target, 0, goal_text)

            await self.goal_repository.save_goal(new_goal)
            return new_goal
        except Exception:
            return None