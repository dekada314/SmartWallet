from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class Keyaboards:
    @staticmethod
    def get_all_func_buttons() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Твоя статистика")],
                [
                    KeyboardButton(text="Ввести расход"),
                    KeyboardButton(text="Ввести доход"),
                ],
            ],
            resize_keyboard=True,
        )

    @staticmethod
    def get_all_analytics_buttons() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="За день"), KeyboardButton(text="За неделю")],
                [KeyboardButton(text="За месяц"), KeyboardButton(text="За год")],
            ],
            resize_keyboard=True,
        )
