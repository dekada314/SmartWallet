from aiogram.types import Message

from domain.entities.goal import Goal
from repository.base_goals_repository import BaseGoalsRepository


class ChangeGoalDescUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: Message, goal_id: int):
        goal: Goal = await self.goal_repository.get_goal_attrs(
            message.from_user.id, goal_id
        )
        try:
            goal.text = message.text
            await self.goal_repository.change_goal_text(goal)
            return goal
        except ValueError:
            print("бе")
            
