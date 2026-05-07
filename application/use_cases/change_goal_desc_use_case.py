from aiogram.types import Message

from app.core.logs_config.logger_wrappers import use_case_logger
from domain.entities.goal import Goal
from domain.repositories.base_goals_repository import BaseGoalsRepository


class ChangeGoalDescUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    @use_case_logger
    async def execute(self, message: Message, goal_id: int) -> None:
        if not message.text or not message.from_user:
            return

        user_id = message.from_user.id

        await self.goal_repository.change_goal_text(user_id, goal_id, message.text)

