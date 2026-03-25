from aiogram.types import Message

from repository.base_goals_repository import BaseGoalsRepository


class ExceedingTheLimitUseCase:
    def __init__(self, goal_db: BaseGoalsRepository):
        self.goal_db = goal_db

    async def execute(self, message: Message) -> bool:
        count_of_goals = await self.goal_db.get_user_goals_count(message.from_user.id)
        if count_of_goals == 5:
            return False
        return True
