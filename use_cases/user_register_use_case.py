from domain.entities.user import User
from repository.base_user_repository import BaseUserRepository


class UserRegisterUseCase:
    def __init__(self, user_repository: BaseUserRepository):
        self.user_repository = user_repository
        
    async def execute(self, user_id: int, user_name: str) -> User:
        user = await self.user_repository.get_user_by_user_id(user_id)
        if user:
            return user
        
        new_user = User(
            user_id,
            user_name,
            balance = 0
        )
        
        await self.user_repository.save_user(new_user)
    
        return new_user