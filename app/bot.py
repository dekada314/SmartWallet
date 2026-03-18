# python3 -m app.bot

import asyncio
import datetime
import os
import uuid

import yaml
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

from model.model import SkClassifier
from utils.text_processing import noun_searcher, number_searcher

load_dotenv()

YAML_CATEGORIES = "SmartWallet/knowledge_base/categories.yml"
YAML_USERS = "SmartWallet/knowledge_base/users.yml"


bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

main_router = Router()
expense_router = Router()

reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Твоя статистика")],
        [KeyboardButton(text="Ввести расход"), KeyboardButton(text="Ввести доход")],
        [KeyboardButton(text="Помощь")],
        [KeyboardButton(text="еда")],
    ],
    resize_keyboard=True,
)

inline_keyboad = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Открыть сайт", url="https://www.wildberries.by")]
    ]
)


class ExpenseForm(StatesGroup):
    waiting_for_callback = State()


def get_users() -> dict:
    with open(YAML_USERS, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_categories() -> dict:
    with open(YAML_CATEGORIES, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["categories"]


def create_user(user_id: int, user_first_name: str) -> None:
    data = get_users()
    if not data["users"].get(user_id, 0):
        user = {
            "categories": {
                "food": [],
                "transport": [],
                "education": [],
                "entertainment": [],
            },
            "name": user_first_name,
        }
        data["users"][user_id] = user
        with open(YAML_USERS, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, allow_unicode=True)
    return


@main_router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    create_user(user_id=user_id, user_first_name=first_name)

    await message.answer(
        f"Привет, {first_name}! Я бот 💰\n\n"
        "Доступные команды:\n"
        "/start - Главное меню\n"
        "/info - Информация о боте\n"
        "/stats - Показать статистику\n\n"
        "Или используй кнопки ниже ⬇️",
        reply_markup=reply_keyboard,
    )


@main_router.message(Command("info"))
async def info_handler(message: types.Message):
    await message.answer(
        "Я буду твоим персональным помощником по финансам."
        " Нажми /start, чтобы ознакомться с моими возможностями"
    )


@main_router.message(lambda message: message.text == "Твоя статистика")
async def stats(message: types.Message):
    await message.answer("Твоя статистика пока пуста")


def create_transaction(
    category: str, amount: float, type: str, description: str = ""
) -> dict[int | float : str]:
    return {
        "transaction_id": str(uuid.uuid4()),
        "data": datetime.datetime.now().strftime("%B %d %Y - %H:%M:%S"),
        "category": category,
        "amount": float(amount),
        "type": type,
        "description": description,
    }


# -------------- Enter expense with category recogniser --------------
@expense_router.message(lambda message: message.text == "Ввести расход")
async def enter_expense(message: types.Message, state: FSMContext):
    await message.answer("Введите расход:")
    await state.set_state(ExpenseForm.waiting_for_callback)


@expense_router.message(ExpenseForm.waiting_for_callback)
async def process_enter_expense(message: types.Message, state: FSMContext):
    amount = number_searcher(message.text)
    noun = noun_searcher(message.text)[0]

    categories = get_categories()

    output_category = None
    for category, data in categories.items():
        if noun in data.get("keywords", []):
            output_category = category

    if not output_category:
        model = SkClassifier()
        model.retrain()
        predict_category, prob = model.predict(noun)
        await message.answer(f"Я уверен то что это {predict_category} на {prob}")
        if prob > 0.7:
            output_category = predict_category

    await message.answer(f"{amount=}, {output_category=}")


@dp.message(lambda message: message.text == "Помощь")
async def help(message: types.Message):
    await message.answer("Вот полезные ссылки: ", reply_markup=inline_keyboad)


@dp.message(lambda message: message.text == "еда")
async def food(message: types.Message):
    with open(YAML_CATEGORIES, "r") as file:
        categories = yaml.safe_load(file)
    await message.answer(categories["categories"]["food"]["description"])


# @dp.message()
# async def unknown_command(message: types.Message):
#     await message.answer("Такой команды нет")

dp.include_router(main_router)
dp.include_router(expense_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
