from aiogram.types import Message

from domain.entities.goal import Goal
from repository.base_goals_repository import BaseGoalsRepository


class UpdateGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, message: Message, goal_id: int):
        goal: Goal = await self.goal_repository.get_goal_attrs(
            message.from_user.id, goal_id
        )
        try:
            new_bill = float(message.text)
            is_goal_achieved = goal.add_amount(new_bill)
            if is_goal_achieved is None:
                await self.goal_repository.update_goal(goal)
                return goal

            await self.goal_repository.delete_goal(goal)
            return is_goal_achieved

        except ValueError:
            print("Ввод должен быть неотрицательным")
