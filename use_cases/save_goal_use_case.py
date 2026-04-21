from aiogram.types import Message

from domain.entities.goal import Goal
from domain.entities.user import User
from handlers.save_goal_request import SaveGoalRequest
from repository.base_goals_repository import BaseGoalsRepository


class SaveGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, dto: SaveGoalRequest) -> User:
        user_id = dto.user_id
        last_user_goal_id = await self.goal_repository.get_last_id(user_id)
        try:
            new_goal = Goal(user_id, last_user_goal_id + 1, dto.amount, 0, dto.text)

            await self.goal_repository.save_goal(new_goal)
            return new_goal
        except Exception:
            return None
