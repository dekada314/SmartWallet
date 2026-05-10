from abc import ABC, abstractmethod

from domain.entities.goal import Goal


class BaseGoalsRepository:
    @abstractmethod
    async def get_order_number_for_user(self, user_id: int) -> int: ...

    @abstractmethod
    async def save_goal(self, goal: Goal) -> None: ...

    @abstractmethod
    async def get_all_user_goals(self, user_id: int) -> list[Goal]: ...

    @abstractmethod
    async def get_goal_attrs(self, user_id: int, order_number: int) -> Goal: ...

    @abstractmethod
    async def update_goal(self, goal: Goal) -> None: ...

    @abstractmethod
    async def delete_goal(self, goal: Goal) -> None: ...

    @abstractmethod
    async def change_goal_text(
        self, user_id: int, order_number: int, new_text: str
    ) -> None: ...

    @abstractmethod
    async def get_user_goals_count(self, user_id: int) -> int: ...

    @abstractmethod
    async def get_users(self) -> None: ...
