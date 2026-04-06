from aiogram import Router, types

from use_cases.give_advice_use_case import GiveAdviceUseCase


class AdviceHandler:
    def __init__(self, give_advice_us: GiveAdviceUseCase):
        self.give_advice_us = give_advice_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Получить совет")
        async def handle_advice_button(message: types.Message):
            advice = self.give_advice_us.execute()
            await message.answer(advice)