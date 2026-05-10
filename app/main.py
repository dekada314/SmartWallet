import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

import app.config.settings as settings
from app.bot.handlers.advice_handler import AdviceHandler
from app.bot.handlers.base_handler import BaseHandler
from app.bot.handlers.expense_handler import ExpenseHandler
from app.bot.handlers.goal_handler import GoalHandler
from app.bot.handlers.income_handler import IncomeHandler
from app.bot.handlers.statistics_handler import StatisticsHandler
from app.core.logs_config.logger import LogManager
from application.use_cases.add_expense_user_case import AddExpenseUseCase
from application.use_cases.add_income_use_case import AddIncomeUseCase
from application.use_cases.change_goal_desc_use_case import ChangeGoalDescUseCase
from application.use_cases.delete_goal_use_case import DeleteGoalUseCase
from application.use_cases.display_user_goals_use_case import DisplayUserGoals
from application.use_cases.exceeding_the_limit_use_case import ExceedingTheLimitUseCase
from application.use_cases.get_statistics_use_case import GetStatiscticsPerPeriod
from application.use_cases.give_advice_use_case import GiveAdviceUseCase
from application.use_cases.save_goal_use_case import SaveGoalUseCase
from application.use_cases.update_goal_use_case import UpdateGoalUseCase
from application.use_cases.user_register_use_case import UserRegisterUseCase
from infrastructure.database.implementations.sqlite_goals_repository import (
    SqliteGoalsRepository,
)
from infrastructure.database.implementations.sqlite_transaction_repository import (
    SQLiteTransactionRepository,
)
from infrastructure.database.implementations.sqlite_user_repository import (
    SQLiteUserRepository,
)
from infrastructure.external_services.get_categories import GetCategories
from infrastructure.external_services.receipt_parser import ReceiptParser
from infrastructure.external_services.sheduler import APSCheduler
from infrastructure.knowledge_base.implementations.yaml_advices_repository import (
    YamlAdvicesRepository,
)
from infrastructure.knowledge_base.implementations.yaml_categories_repository import (
    YamlCategoriesRepository,
)
from infrastructure.ml.embeddings.text_processing import TextProcessing


async def main():
    logger = LogManager()
    logger.setup()

    user_db = SQLiteUserRepository(settings.DB)
    await user_db.init_db()
    transaction_db = SQLiteTransactionRepository(settings.DB)
    await transaction_db.init_db()
    categories_kb = YamlCategoriesRepository(settings.YAML_CATEGORIES)
    advices_kb = YamlAdvicesRepository(settings.YAML_ADVICES)
    goal_db = SqliteGoalsRepository(settings.DB)
    await goal_db.init_db()

    text_processing = TextProcessing(
        cat_examples=categories_kb.get_all_categories_examples()
    )

    add_expense_us = AddExpenseUseCase(
        transaction_db, categories_kb, user_db, text_processing
    )
    register_us = UserRegisterUseCase(user_db)
    change_goal_us = ChangeGoalDescUseCase(goal_db)
    delete_goal_us = DeleteGoalUseCase(goal_db)
    save_goal_us = SaveGoalUseCase(goal_db)
    display_goals_us = DisplayUserGoals(goal_db)
    update_goal_us = UpdateGoalUseCase(goal_db)
    exceeding_limits_us = ExceedingTheLimitUseCase(goal_db)
    add_income_us = AddIncomeUseCase(user_db, transaction_db)
    give_advice_us = GiveAdviceUseCase(advices_kb)
    get_categories = GetCategories(categories_kb)
    receipt_parser = ReceiptParser(categories_kb)
    statistics_us = GetStatiscticsPerPeriod(transaction_db)

    base_handler = BaseHandler(register_us)
    base_handler.register()
    expense_handler = ExpenseHandler(add_expense_us, get_categories, receipt_parser)
    expense_handler.register()
    goal_handler = GoalHandler(
        save_goal_us,
        display_goals_us,
        update_goal_us,
        delete_goal_us,
        change_goal_us,
        exceeding_limits_us,
    )
    goal_handler.register()
    income_handler = IncomeHandler(add_income_us)
    income_handler.register()
    advice_handler = AdviceHandler(give_advice_us)
    advice_handler.register()
    statistics_handler = StatisticsHandler(statistics_us)
    statistics_handler.register()

    bot = Bot(os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    scheduler = APSCheduler(goal_db, bot)
    scheduler.start()

    dp.include_router(base_handler.router)
    dp.include_router(expense_handler.router)
    dp.include_router(goal_handler.router)
    dp.include_router(income_handler.router)
    dp.include_router(advice_handler.router)
    dp.include_router(statistics_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
