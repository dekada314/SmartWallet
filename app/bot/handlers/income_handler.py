from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pydantic import ValidationError

from app.dto.requests.save_income_request import SaveIncomeRequest
from application.exceptions.exceptions import GettingUserError
from application.use_cases.add_income_use_case import AddIncomeUseCase


class IncomeForm(StatesGroup):
    waiting_for_earning = State()


class IncomeHandler:
    def __init__(self, add_income_us: AddIncomeUseCase):
        self.add_income_us = add_income_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Ввести доход")
        async def handle_income_button(message: types.Message, state: FSMContext):
            await message.answer("Введите сколько удалось заработать:")
            await state.set_state(IncomeForm.waiting_for_earning)

        @self.router.message(IncomeForm.waiting_for_earning)
        async def handle_income_expression(message: types.Message):
            try:
                income_dto = SaveIncomeRequest(
                    user_id=message.from_user.id, amount=message.text
                )
                new_balance = await self.add_income_us.execute(income_dto=income_dto)
                if new_balance:
                    await message.answer(
                        f"Ваше новое значение баланса {new_balance:.0f}"
                    )
            except ValidationError as e:
                await message.answer(f"Возникла ошибка: {e}")
            except GettingUserError:
                await message.answer(f"Для начала зарегистрируйтесь через /start")
