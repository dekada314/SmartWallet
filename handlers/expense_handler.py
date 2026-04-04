from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.markdown import hbold, hcode, hitalic, hlink

from keyboards import Keyboards
from services.get_categories import GetCategories
from use_cases.add_expense_user_case import AddExpenseUseCase


class ExpenseForm(StatesGroup):
    waiting_for_callback = State()
    waiting_for_category = State()
    waiting_for_amount = State()


class ExpenseHandler:
    def __init__(self, add_expense_us: AddExpenseUseCase, get_categories: GetCategories):
        self.get_categories = get_categories
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
                
        # --------------------------
                
        @self.router.callback_query(F.data == "enter_by_buttons")
        async def enter_by_buttons(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            all_categories = self.get_categories.get_categories_names()
            
            main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text = text)] for text in all_categories
            ],resize_keyboard=True)
            await callback.message.answer("Выберите категорию:", reply_markup=main_keyboard)
            await state.set_state(ExpenseForm.waiting_for_category)
            
        @self.router.message(ExpenseForm.waiting_for_category)
        async def handle_category_by_user(message: types.Message, state: FSMContext):
            user_category = message.text
            await state.update_data(user_category = user_category)
            await message.answer("Введите сумму затраты")
            await state.set_state(ExpenseForm.waiting_for_amount)
            
        @self.router.message(ExpenseForm.waiting_for_amount)
        async def handle_category_with_amount(message: types.Message, state: FSMContext):
            amount = message.text
            
            data = await state.get_data()
            user_category = data.get("user_category")
            
            transaction = await self.add_expense_us.execute(
                message.from_user.id, amount, user_category
            )
            
            if transaction:
                await message.answer(
                    f"🏦 <b>Ваша транзакция</b> \n\n"
                    f"<b>Категория:</b> {transaction.category}\n"
                    f"<b>Сумма:</b> {transaction.amount}\n"
                    f"<b>Дата и время:</b> {transaction.created_at.strftime('%d.%m.%Y - %H:%M:%S')}\n",
                    parse_mode="HTML"
                )
                
            await state.clear()
            
            
        # ---------------------
            
        @self.router.callback_query(F.data == "enter_by_check")
        async def enter_by_check(callback: CallbackQuery):
            await callback.answer()