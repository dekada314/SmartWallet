from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold, hcode, hitalic, hlink

from keyboards import Keyboards
from use_cases.add_expense_user_case import AddExpenseUseCase


class ExpenseForm(StatesGroup):
    waiting_for_callback = State()


class ExpenseHandler:
    def __init__(self, add_expense_us: AddExpenseUseCase):
        self.add_expense_us = add_expense_us
        self.router = Router()

    def register(self):
        @self.router.message(lambda message: message.text == "Ввести расход")
        async def handle_expense_button(message: types.Message, state: FSMContext):
            await message.answer(
                "Введите описание транзакции\n\n"
                "<b>Для корректного считывания должно быть хотя бы число и сущетсвительное. Например:</b>\n"
                "<i>купил кофе за 7</i>\n"
                "<i>курсы 300 рублей</i>\n"
                "<i>15 рублей за продукты </i>\n",
                parse_mode="HTML",
            )
            await state.set_state(ExpenseForm.waiting_for_callback)

        @self.router.message(ExpenseForm.waiting_for_callback)
        async def handle_expense_expression(message: types.Message, state: FSMContext):
            try:
                transaction = await self.add_expense_us.execute(
                    message.from_user.id, message.text
                )
                if transaction:
                    await message.answer(
                        f"🏦 <b>Ваша транзакция</b> \n\n"
                        f"<b>Категория:</b> {transaction.category}\n"
                        f"<b>Сумма:</b> {transaction.amount}\n"
                        f"<b>Дата и время:</b> {transaction.created_at.strftime('%d.%m.%Y - %H:%M:%S')}\n",
                        parse_mode="HTML",
                    )
            except:
                await message.answer("Вы некорректно ввели данные!")
            finally:
                await state.clear()
