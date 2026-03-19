from aiogram import Router, types
from aiogram.filters import Command

from keyboards import Keyboards
from use_cases.user_register_use_case import UserRegisterUseCase


class BaseHandler:
    def __init__(self, user_registry_us: UserRegisterUseCase):
        self.user_registry_us = user_registry_us
        self.router = Router()

    def register(self):
        @self.router.message(Command("start"))
        async def handle_start_command(message: types.Message):
            user_id = message.from_user.id
            user_name = message.from_user.first_name

            user = await self.user_registry_us.execute(user_id, user_name)
            if user:
                await message.answer(
                    f"Привет, {user_name}! 👋 Я твой личный калькулятор расходов и секретный хранитель денег\n"
                    "Давай посмотрим, куда сегодня улетят твои рубли 💸… или хотя бы научимся это отслеживать!\n"
                    "Если хочешь ознакомиться с моими командами, то нажимай на /info",
                    reply_markup=Keyboards.get_all_func_buttons(),
                )
            else:
                await message.answer("")

        @self.router.message(Command("info"))
        async def handle_info_command(message: types.Message):
            await message.answer("Что-то блаблаалаб")
