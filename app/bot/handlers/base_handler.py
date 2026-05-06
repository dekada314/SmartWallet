from aiogram import Router, types
from aiogram.filters import Command
from pydantic import ValidationError

from app.bot.keyboards.keyboards import Keyboards
from app.bot.middleware.start_middleware import StartMiddleware
from app.dto.requests.user_registry_request import UserRegistryRequest
from app.dto.responses.user_response import UserResponse
from application.use_cases.user_register_use_case import UserRegisterUseCase


class BaseHandler:
    def __init__(self, user_registry_us: UserRegisterUseCase):
        self.user_registry_us = user_registry_us
        self.router = Router(name="start_and_info_router")

    def register(self):
        # self.router.message.middleware(StartMiddleware())

        @self.router.message(Command("start"))
        async def handle_start_command(message: types.Message):
            try:
                user_registry_request = UserRegistryRequest(
                    user_id=message.from_user.id, user_name=message.from_user.first_name
                )

                user: UserResponse = await self.user_registry_us.execute(
                    user_registry_request
                )
                if user:
                    await message.answer(
                        f"Привет, {user.user_name}! 👋 Я твой личный калькулятор расходов и секретный хранитель денег\n"
                        "Давай посмотрим, куда сегодня улетят твои рубли 💸… или хотя бы научимся это отслеживать!\n"
                        "Если хочешь ознакомиться с моими командами, то нажимай на /info",
                        reply_markup=Keyboards.get_all_func_buttons(),
                    )
                    return user
                await message.answer(
                    "Похоже вы уже зарегистрированы",
                    reply_markup=Keyboards.get_all_func_buttons(),
                )
                return None
            except ValidationError:
                await message.answer(
                    "Мы пока что не можем вас зарегистрировать, вернитесь позже"
                )
