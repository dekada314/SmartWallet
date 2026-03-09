import asyncio
import os

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

YAML_CATEGORIES = '../knowledge_base/categories.yml'


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

@dp.message(Command('start'))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот 💰\n\n"
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
        categories['categories'][0]['id']
    )
    
    
@dp.message()
async def unknown_command(message: types.Message):
    await message.answer("Такой команды нет")

async def main():
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())