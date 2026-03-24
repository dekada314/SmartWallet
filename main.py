import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, Router, types
from dotenv import load_dotenv

import config
from handlers.base_handler import BaseHandler
from handlers.expense_handler import ExpenseHandler
from handlers.goal_handler import GoalHandler
from infrastructure.sqlite_goals_repository import SqliteGoalsRepository
from infrastructure.sqlite_transaction_repository import SQLiteTransactionRepository
from infrastructure.sqlite_user_repository import SQLiteUserRepository
from infrastructure.yaml_categories_repository import YamlCategoriesRepository
from model.model import SkClassifier
from services.text_processing import TextProcessing
from use_cases.add_expense_user_case import AddExpenseUseCase
from use_cases.change_goal_desc_use_case import ChangeGoalDescUseCase
from use_cases.delete_goal_use_case import DeleteGoalUseCase
from use_cases.display_user_goals_use_case import DisplayUserGoals
from use_cases.give_advice_use_case import GiveAdviceUseCase
from use_cases.save_goal_use_case import SaveGoalUseCase
from use_cases.update_goal_use_case import UpdateGoalUseCase
from use_cases.user_register_use_case import UserRegisterUseCase

load_dotenv()


async def main():
    user_db = SQLiteUserRepository(config.SQLITE_USERS)
    await user_db.init_db()
    transaction_db = SQLiteTransactionRepository(config.SQLITE_TRANSACTIONS)
    await transaction_db.init_db()
    categories_kb = YamlCategoriesRepository(config.YAML_CATEGORIES)
    goal_db = SqliteGoalsRepository(config.SQLITE_GOALS)
    await goal_db._init_db()

    ml_model = SkClassifier(
        config.DATASET_PATH, config.VECTORIZER_PATH, config.MODEL_PATH
    )

    add_expense_us = AddExpenseUseCase(transaction_db, categories_kb, user_db, ml_model)
    register_us = UserRegisterUseCase(user_db)
    advice_us = GiveAdviceUseCase()
    change_goal_us = ChangeGoalDescUseCase(goal_db)
    delete_goal_us = DeleteGoalUseCase(goal_db)
    save_goal_us = SaveGoalUseCase(goal_db)
    display_goals_us = DisplayUserGoals(goal_db)
    update_goal_us = UpdateGoalUseCase(goal_db)

    base_handler = BaseHandler(register_us)
    base_handler.register()
    expense_handler = ExpenseHandler(add_expense_us)
    expense_handler.register()
    goal_handler = GoalHandler(save_goal_us, display_goals_us, update_goal_us, delete_goal_us, change_goal_us)
    goal_handler.register()

    bot = Bot(os.getenv("TOKEN"))
    dp = Dispatcher()

    dp.include_router(base_handler.router)
    dp.include_router(expense_handler.router)
    dp.include_router(goal_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
