from domain.entities.user import User
from repository.base_goals_repository import BaseGoalsRepository


class SaveGoalUseCase:
    def __init__(self, goal_repository: BaseGoalsRepository):
        self.goal_repository = goal_repository
 
    async def execute(self, user_id: int, text: str) -> User:
        await self.goal_repository.save_goal(user_id, text)
