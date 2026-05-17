from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from pydantic import ValidationError

from app.bot.keyboards.keyboards import Keyboards
from app.dto.requests.save_transaction_request import SaveTransactionRequest
from app.dto.responses.transaction_response import TransactionReponse
from application.use_cases.add_expense_user_case import AddExpenseUseCase
from domain.entities.transaction import Transaction
from infrastructure.external_services.get_categories import GetCategories
from infrastructure.external_services.receipt_parser import ReceiptParser

from ..middleware.finance_middleware import FinanceMiddleware


class ExpenseForm(StatesGroup):
    waiting_text_input = State()
    waiting_for_user_input = State()
    waiting_for_doc_input = State()


class ButtonsInputForm(StatesGroup):
    waiting_for_category = State()


class ExpenseHandler:
    def __init__(
        self,
        add_expense_us: AddExpenseUseCase,
        get_categories: GetCategories,
        receipt_parser: ReceiptParser,
    ):
        self.get_categories = get_categories
        self.add_expense_us = add_expense_us
        self.receipt_parser = receipt_parser
        self.router = Router(name="expense_router")

    def register(self):
        self.router.message.middleware(FinanceMiddleware())
        self.router.callback_query.middleware(FinanceMiddleware())

        def _transaction_format(transaction: Transaction):
            return (
                f"🏦 <b>Ваша транзакция</b> \n\n"
                f"<b>Категория:</b> {transaction.category}\n"
                f"<b>Сумма:</b> {transaction.amount}\n"
                f"<b>Дата и время:</b> {transaction.created_at.strftime('%d.%m.%Y - %H:%M:%S')}\n"
            )

        @self.router.message(lambda message: message.text == "Ввести расход")
        async def handle_expense_button(message: types.Message, state: FSMContext):
            await message.answer(
                "<b>Выберите тип ввода:</b>",
                reply_markup=Keyboards.get_enter_expense_buttons(),
                parse_mode="HTML",
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
            await state.set_state(ExpenseForm.waiting_text_input)

        @self.router.message(ExpenseForm.waiting_text_input)
        async def handle_enter_by_text(message: types.Message, state: FSMContext):
            try:
                transaction_request = SaveTransactionRequest(
                    user_id=message.from_user.id, text=message.text
                )

                transaction_response: TransactionReponse = (
                    await self.add_expense_us.execute(transaction_request)
                )

                if transaction_response:
                    await message.answer(
                        _transaction_format(transaction_response.transaction),
                        parse_mode="HTML",
                    )
                if transaction_response.warnings:
                    for warning in transaction_response.warnings:
                        await message.answer(warning)

            except ValidationError:
                await message.answer("Вы некорректно ввели данные!")
            finally:
                await state.clear()

            return (
                ("EXPENSE", transaction_response.transaction.amount)
                if transaction_response
                else None
            )

        # --------------------------

        @self.router.callback_query(F.data == "enter_by_buttons")
        async def handle_enter_by_buttons(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            all_categories = self.get_categories.get_categories_names()

            main_keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=text)] for text in all_categories],
                resize_keyboard=True,
            )
            await callback.message.answer(
                "Выберите категорию:", reply_markup=main_keyboard
            )
            await state.set_state(ButtonsInputForm.waiting_for_category)

        @self.router.message(ButtonsInputForm.waiting_for_category)
        async def handle_category_by_user(message: types.Message, state: FSMContext):
            user_category = message.text
            await state.update_data(user_category=user_category)
            await message.answer("Введите сумму затраты")
            await state.set_state(ExpenseForm.waiting_for_user_input)

        @self.router.message(ExpenseForm.waiting_for_user_input)
        async def handle_category_with_amount(
            message: types.Message, state: FSMContext
        ):
            amount = message.text

            data = await state.get_data()
            user_category = data.get("user_category")

            transaction_response = SaveTransactionRequest(
                user_id=message.from_user.id, text=amount, category=user_category
            )

            transaction_response: TransactionReponse = (
                await self.add_expense_us.execute(transaction_response)
            )

            if transaction_response:
                await message.answer(
                    _transaction_format(transaction_response.transaction),
                    parse_mode="HTML",
                )
            if transaction_response.warnings:
                for warning in transaction_response.warnings:
                    await message.answer(warning)

            await state.clear()
            return (
                ("EXPENSE", transaction_response.transaction.amount)
                if transaction_response
                else None
            )

        # ---------------------

        @self.router.callback_query(F.data == "enter_by_check")
        async def enter_by_check(callback: CallbackQuery, state: FSMContext):
            await callback.answer()
            await callback.message.answer("Присылайте фото/файл вашего чека!")
            await state.set_state(ExpenseForm.waiting_for_doc_input)

        # @self.router.message(ExpenseForm.waiting_for_doc_input, F.photo)
        # async def handle_enter_by_photo(message: types.Message, state: FSMContext):
        #     photo = message.photo[-1]
        #     file = await message.bot.get_file(photo.file_id)

        #     file_path = f"receipts/receipt{message.from_user.id}_{photo.file_unique_id}.jpg"
        #     await message.bot.download_file(file.file_path, destination=file_path)

        #     try:
        #         parsed_data = self.receipt_parser.parse_file(file_path)
        #         await message.answer(parsed_data["category"] + str(parsed_data["amount"]))
        #     except Exception as e:
        #         await message.answer(f"Произошла ошибка при чтении: {e}")

        @self.router.message(ExpenseForm.waiting_for_doc_input, F.document)
        async def handle_enter_by_file(message: types.Message, state: FSMContext):
            await message.answer("Пока не реализовано")
            return
            document = message.document
            file = await message.bot.get_file(document.file_id)
            file_ext = (
                document.file_name.split(".")[-1].lower() if document.file_name else ""
            )

            file_path = f"assets/receipts/receipt{message.from_user.id}_{document.file_unique_id}.{file_ext}"
            await message.bot.download_file(file.file_path, destination=file_path)

            try:
                parsed_data = self.receipt_parser.parse_file(file_path)
                transaction_request = SaveTransactionRequest(
                    user_id=message.from_user.id,
                    text=str(parsed_data["amount"]),
                    category=parsed_data["category"],
                )

                await state.update_data(operation_type="expense")

                transaction_response: TransactionReponse = (
                    await self.add_expense_us.execute(transaction_request)
                )

                if transaction_response:
                    await message.answer(
                        _transaction_format(transaction_response.transaction),
                        parse_mode="HTML",
                    )
                if transaction_response.warnings:
                    for warning in transaction_response.warnings:
                        await message.answer(warning)

            except ValidationError:
                await message.answer("❌ Неверный формат ввода")
                raise
