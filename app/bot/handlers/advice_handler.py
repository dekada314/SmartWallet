from aiogram import Router, types

from app.dto.responses.advice_reponse import AdviceModel
from application.use_cases.give_advice_use_case import GiveAdviceUseCase


class AdviceHandler:
    def __init__(self, give_advice_us: GiveAdviceUseCase):
        self.give_advice_us = give_advice_us
        self.router = Router(name="advice_router")

    def register(self):
        def _advice_output(response: AdviceModel):
            return f"<b>{response.name}</b>\n\n{response.desc}"

        @self.router.message(lambda message: message.text == "Получить совет")
        async def handle_advice_button(message: types.Message):
            advice_reponse = await self.give_advice_us.execute()
            await message.answer(_advice_output(advice_reponse))
