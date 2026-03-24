from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class Keyboards:
    @staticmethod
    def get_all_func_buttons() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Твоя статистика")],
                [
                    KeyboardButton(text="Ввести расход"),
                    KeyboardButton(text="Ввести доход"),
                ],
                [KeyboardButton(text="Цели"), KeyboardButton(text="Аналитика")],
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

    @staticmethod
    def get_all_goals_buttons() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Добавить цель", callback_data="save_goal"
                    ),
                    InlineKeyboardButton(text="Удалить цель", callback_data="del_goal"),
                ],
                [
                    InlineKeyboardButton(
                        text="Просмотреть цели", callback_data="display_goals"
                    ),
                    InlineKeyboardButton(
                        text="Настроить цели", callback_data="set_up_goal"
                    ),
                ],
            ],
        )

    @staticmethod
    def get_update_goal_button(goal_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Добавить к цели", callback_data=f"update_goal_{goal_id}"
                    )
                ]
            ]
        )
