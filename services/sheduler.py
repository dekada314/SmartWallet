from datetime import datetime

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from repository.base_goals_repository import BaseGoalsRepository


class APSCheduler:
    def __init__(self, db: BaseGoalsRepository, bot: Bot):
        self.db = db
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(self._tick, "cron", hour=9, minute=28, max_instances=1)
        self.scheduler.start()

    async def _tick(self) -> None:
        users_id = await self.db.get_users()
        for user in users_id:
            user_goals = await self.db.get_all_user_goals(user)
            output = "Напоминаю о ваших целях:\n\n"
            for index, data in enumerate(user_goals):
                output += (
                    f"<b>{index}. {data[0]}: {data[2] / data[1] * 100:.1f}к%</b>\n"
                )
            await self._send_message(user, output)

    async def _send_message(self, user_id: int, text: str):
        await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
