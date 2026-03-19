from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from use_cases.notification_use_case import NotificationUseCase


class TimeForm(StatesGroup):
    waiting_for_time = State


class GoalsHandler:
    def __init__(self, notification_us: NotificationUseCase):
        self.notification_us = notification_us
        self.router = Router()

    def register(self):
        @self.router.message(Command(["set_notifier_time"]))
        async def goals_notifier(message: types.Message, state: FSMContext):
            await message.answer(
                "Введите время желаемых напоминай о целях, если не хотите их получать введите 0"
            )
            await state.set_state(TimeForm.waiting_for_time)
