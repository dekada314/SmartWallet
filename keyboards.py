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
                [KeyboardButton(text="Статистика")],
                [
                    KeyboardButton(text="Ввести расход"),
                    KeyboardButton(text="Ввести доход"),
                ],
                [KeyboardButton(text="Цели"), KeyboardButton(text="Получить совет")],
            ],
            resize_keyboard=True,
        )

    @staticmethod
    def get_all_statistics_buttons() -> InlineKeyboardButton:
        return InlineKeyboardButton(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="За день", callback_data="per_day"),
                    InlineKeyboardButton(text="За неделю", callback_data="per_week"),
                ],
                [
                    InlineKeyboardButton(text="За месяц", callback_data="per_month"),
                    InlineKeyboardButton(text="За год", callback_data="per_year"),
                ],
            ],
        )

    @staticmethod
    def get_all_goals_buttons() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить цель", callback_data="save_goal")],
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

    @staticmethod
    def get_setup_goal_button(goal_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Удалить цель", callback_data=f"del_goal_{goal_id}"
                    ),
                    InlineKeyboardButton(
                        text="Поменять описание цели",
                        callback_data=f"update_desc_{goal_id}",
                    ),
                ]
            ]
        )

    @staticmethod
    def get_enter_expense_buttons() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Ввести сообщением", callback_data=f"enter_by_text"
                    ),
                    InlineKeyboardButton(
                        text="Выбрать категорию вручную",
                        callback_data=f"enter_by_buttons",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Сбросить чек", callback_data="enter_by_check"
                    )
                ],
            ]
        )
