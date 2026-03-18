import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, Router, types
from dotenv import load_dotenv

import config
from handlers.base_handler import BaseHandler
from handlers.expense_handler import ExpenseHandler
from infrastructure.sqlite_transaction_repository import SQLiteTransactionRepository
from infrastructure.sqlite_user_repository import SQLiteUserRepository
from infrastructure.yaml_categories_repository import YamlCategoriesRepository
from model.model import SkClassifier
from services.text_processing import TextProcessing
from use_cases.add_expense_user_case import AddExpenseUseCase
from use_cases.give_advice_use_case import GiveAdviceUseCase
from use_cases.user_register_use_case import UserRegisterUseCase

load_dotenv()


async def main():
    user_db= SQLiteUserRepository(config.SQLITE_USERS)
    transaction_db= SQLiteTransactionRepository(config.SQLITE_TRANSACTIONS) 
    categories_kb = YamlCategoriesRepository(config.YAML_CATEGORIES)
    
    ml_model = SkClassifier(config.DATASET_PATH, config.VECTORIZER_PATH, config.MODEL_PATH)
    
    add_expense_us = AddExpenseUseCase(transaction_db, categories_kb, ml_model)
    register_us = UserRegisterUseCase(user_db)
    advice_us = GiveAdviceUseCase()

    base_handler = BaseHandler(register_us)
    base_handler.register()
    expense_handler = ExpenseHandler(add_expense_us)
    expense_handler.register()

    bot = Bot(os.getenv("TOKEN"))
    dp = Dispatcher()
    
    dp.include_router(base_handler.router)
    dp.include_router(expense_handler.router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
    
if __name__ == "__main__":
    asyncio.run(main())