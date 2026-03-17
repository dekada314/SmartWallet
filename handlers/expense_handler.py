from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import Keyaboards
from use_cases.add_expense_user_case import AddExpenseUseCase


class ExpenseForm(StatesGroup):
    waiting_for_callback = State()


class ExpenseHandler:
    def __init__(self, add_expense_us: AddExpenseUseCase):
        self.add_expense_us = add_expense_us
        self.router = Router()
        self._handle_registry()

    def _handle_registry(self):

        @self.router.message(lambda message: message.text == "Внести расход")
        async def handle_expense_button(message: types.Message, state: FSMContext):
            await message.answer("Введите сообщение:")
            await state.set_state(ExpenseForm.waiting_for_callback)
            
        @self.router.message(ExpenseForm.waiting_for_callback)
        async def handle_expense_expression(message: types.Message, state: FSMContext):
            # допилить бд транзакций, разобраться с праймари кеями, пересмотреть логику use case, сделать сервисы по анализу текста
            ...