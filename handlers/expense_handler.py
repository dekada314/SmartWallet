from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
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
                "<b>Выберите тип ввода:</b>",
                reply_markup=Keyboards.get_enter_expense_buttons(),
                parse_mode="HTML"
            )
            
        @self.router.callback_query(F.data == "enter_by_text")
        async def enter_by_text(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            await callback.message.answer(
                "Введите описание транзакции\n\n"
                "<b>Для корректного считывания должно быть хотя бы число и сущетсвительное. Например:</b>\n"
                "<i>купил кофе за 7</i>\n"
                "<i>курсы 300 рублей</i>\n"
                "<i>15 рублей за продукты </i>\n",
                parse_mode="HTML",
            )
            await state.set_state(ExpenseForm.waiting_for_callback)

        @self.router.message(ExpenseForm.waiting_for_callback)
        async def handle_enter_by_text(message: types.Message, state: FSMContext):
            await state.clear()
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
                
        @self.router.callback_query(F.data == "enter_by_buttons")
        async def enter_by_buttons(callback: CallbackQuery):
            await callback.answer()
            
        @self.router.callback_query(F.data == "enter_by_check")
        async def enter_by_check(callback: CallbackQuery):
            await callback.answer()