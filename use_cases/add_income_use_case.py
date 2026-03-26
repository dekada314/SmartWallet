from typing import Union

from aiogram.types import Message

from domain.entities.transaction import Transaction
from domain.entities.user import User
from repository.base_user_repository import BaseUserRepository

from .exceptions import GettingUserError, NotValidAmountError


class AddIncomeUseCase:
    def __init__(
        self,
        user_repository: BaseUserRepository,
    ):
        self.user_repository = user_repository

    def _parse_amount(self, text: str) -> float:
        try:
            parsed_amount = float(text.replace(",", ".").strip("$ "))
        except ValueError:
            raise NotValidAmountError

        return parsed_amount

    async def execute(self, message: Message) -> None | float:
        if not message.text or not message.from_user:
            return

        user_id = message.from_user.id
        user: User = await self.user_repository.get_user_by_user_id(user_id)

        if not user:
            raise GettingUserError

        try:
            income_amount = self._parse_amount(message.text)
            user.add_amount(income_amount)
            user.update_last_action()
            await self.user_repository.save_user(user)
            return user.balance

        except Exception as e:
            raise ValueError('asd')
