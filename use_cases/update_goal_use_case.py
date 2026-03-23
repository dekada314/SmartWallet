from domain.entities.user import User
from repository.base_goals_repository import BaseGoalsRepository


class UpdateGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository

    async def execute(self, user_id: int, goal_id: int, curr_bill: float) -> User:
        await self.goal_repository.update_goal(user_id, goal_id, curr_bill)
         
        # data = self.goal_repository.get_goal_attrs()
        # if data['curr_bill'] >= data["target"]:
        #     await self.goal_repository
