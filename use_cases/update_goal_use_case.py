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
        new_bill = float(message.text)
        is_goal_achieved = goal.add_amount(new_bill)
        if is_goal_achieved:
            await self.goal_repository.delete_goal(goal.user_id, goal.user_goal_id)

        await self.goal_repository.update_goal(
            goal.user_id, goal.user_goal_id, goal.curr_bill
        )
