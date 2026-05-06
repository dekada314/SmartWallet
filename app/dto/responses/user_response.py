from datetime import datetime

from pydantic import BaseModel, Field

from domain.entities.user import User


class UserResponse(BaseModel):
    user_id: int
    user_name: str
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            user_id=user.user_id, user_name=user.user_name, created_at=user.created_at
        )
