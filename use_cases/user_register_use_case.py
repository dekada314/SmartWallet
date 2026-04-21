from datetime import datetime

from domain.entities.user import User
from handlers.user_registry_request import UserRegistryRequest
from repository.base_user_repository import BaseUserRepository


class UserRegisterUseCase:
    def __init__(self, user_repository: BaseUserRepository):
        self.user_repository = user_repository

    async def execute(self, dto: UserRegistryRequest) -> User:
        user = await self.user_repository.get_user_by_user_id(dto.user_id)
        if user:
            return None

        new_user = User(
            user_id=dto.user_id,
            user_name=dto.user_name,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            balance=0,
        )

        await self.user_repository.save_user(new_user)

        return new_user
