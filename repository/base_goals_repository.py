from abc import ABC, abstractmethod


class BaseGoalsRepository:
    @abstractmethod
    async def save_goal() -> None: ...
    @abstractmethod
    async def get_all_user_goals() -> None: ...
