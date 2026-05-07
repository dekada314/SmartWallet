from datetime import datetime

from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.user_registry_request import UserRegistryRequest
from app.dto.responses.user_response import UserResponse
from domain.entities.user import User
from domain.repositories.base_user_repository import BaseUserRepository


class UserRegisterUseCase:
    def __init__(self, user_repository: BaseUserRepository):
        self.user_repository = user_repository

    @use_case_logger
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
        return UserResponse.from_domain(new_user)
