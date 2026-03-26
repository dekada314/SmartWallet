from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold, hcode, hitalic, hlink

from keyboards import Keyboards
from use_cases.add_income_use_case import AddIncomeUseCase


class IncomeForm(StatesGroup):
    waiting_for_callback = State()


class IncomeHandler:
    def __init__(self, add_income_us: AddIncomeUseCase):
        self.add_income_us = add_income_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Ввести доход")
        async def handle_income_button(message: types.Message, state: FSMContext):
            await message.answer("Введите сколько удалось заработать:")
            await state.set_state(IncomeForm.waiting_for_callback)

        @self.router.message(IncomeForm.waiting_for_callback)
        async def handle_income_expression(message: types.Message, state: FSMContext):
            try:
                new_balance = await self.add_income_us.execute(message)
                if new_balance:
                    await message.answer(f"Ваше новое значение баланса {new_balance:.0f}")
            except Exception as e:
                await message.answer(str(e))