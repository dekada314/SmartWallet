from datetime import datetime

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from repository.base_goals_repository import BaseGoalsRepository


class APSCheduler:
    def __init__(self, db: BaseGoalsRepository, bot: Bot):
        self.db = db
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.add_job(self._send_message, "cron", hour=9, minute=0, max_instances=1)
        self.scheduler.start()

    async def _send_message(self):
        pass
