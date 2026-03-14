import asyncio
import datetime
import os
import uuid

import yaml
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

load_dotenv()

YAML_CATEGORIES = 'knowledge_base/categories.yml'
YAML_USERS = 'knowledge_base/users.yml'


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

reply_keyboard = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = "Твоя статистика")],
        [KeyboardButton(text = "Ввести расход"), KeyboardButton(text = "Ввести доход")],
        [KeyboardButton(text = "Помощь")],
        [KeyboardButton(text = "еда")],
    ],
    resize_keyboard = True
)

inline_keyboad = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text = "Открыть сайт", url='https://www.wildberries.by')]
    ]
)

def get_users() -> dict:
    with open(YAML_USERS, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_user(user_id: int, user_first_name: str) -> None:    
    data = get_users()
    if not data['users'].get(user_id, 0):
        user = {
                'categories':
                    {
                        'food': [],
                        'transport': [],
                        'education': [],
                        'entertainment': [],
                    },
                'name': user_first_name
                }
        data['users'][user_id] = user
        with open(YAML_USERS, 'w', encoding='utf-8') as file:
            yaml.safe_dump(data, file, allow_unicode=True)
    return
        
@dp.message(Command('start'))
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
        reply_markup=reply_keyboard
    )
    
@dp.message(Command('info'))
async def info_handler(message: types.Message):
    await message.answer("Я буду твоим персональным помощником по финансам." 
                         " Нажми /start, чтобы ознакомться с моими возможностями")
    
@dp.message(lambda message: message.text == 'Твоя статистика')
async def stats(message: types.Message):
    await message.answer("Твоя статистика пока пуста")
    
def create_transaction(category: str, amount: float, type: str, description: str = "") -> dict[int | float: str] :
    return {
        "transaction_id": str(uuid.uuid4()),
        "data": datetime.datetime.now().strftime('%B %d %Y - %H:%M:%S'),
        "category": category,
        "amount": float(amount),
        "type": type,
        "description": description
    }
    
@dp.message(lambda message: message.text == 'Ввести доход')
async def enter_income(message: types.Message):
    with open(YAML_USERS, 'r') as file:
        users = yaml.safe_load(file)
    curr_category = users['users'][message.from_user.id]['categories']['food']
    
    transaction = create_transaction(
        "food",
        250.0,
        "income",
    )
    curr_category.append(transaction)
    
    with open(YAML_USERS, 'w') as file:
        yaml.safe_dump(users, file, allow_unicode=True)
     
    
@dp.message(lambda message: message.text == 'Помощь')
async def help(message: types.Message):
    await message.answer(
        "Вот полезные ссылки: ",
        reply_markup=inline_keyboad
    )

@dp.message(lambda message: message.text == 'еда')
async def food(message: types.Message):
    with open(YAML_CATEGORIES, 'r') as file:
        categories = yaml.safe_load(file)
    await message.answer(
        categories['categories']['food']['description']
    )
    
# @dp.message()
# async def unknown_command(message: types.Message):
#     await message.answer("Такой команды нет")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())