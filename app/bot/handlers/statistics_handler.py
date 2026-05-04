from aiogram import F, Router, types
from aiogram.filters import Command

from app.bot.keyboards.keyboards import Keyboards
from app.bot.middleware.statistics_middleware import StatisticsMiddleware
from app.dto.requests.get_statistics_request import StatisticsRequest
from app.dto.responses.statistics_reponse import StatisticsResponse
from application.use_cases.enums import PeriodType
from application.use_cases.get_statistics_use_case import GetStatiscticsPerPeriod

callback_to_period = {
    "per_day": PeriodType.DAY,
    "per_week": PeriodType.WEEK,
    "per_mouth": PeriodType.MONTH,
    "per_year": PeriodType.YEAR,
}

period_to_rus_period = {
    PeriodType.DAY: "день",
    PeriodType.WEEK: "неделю",
    PeriodType.MONTH: "месяц",
    PeriodType.YEAR: "год",
}


class StatisticsHandler:
    def __init__(self, analytic_use_case: GetStatiscticsPerPeriod):
        self.analytic_use_case = analytic_use_case
        self.router = Router(name="statistics_router")

    def register(self):
        self.router.message.middleware(StatisticsMiddleware())
        self.router.callback_query.middleware(StatisticsMiddleware())
        
        def _stats_output(text_period, response: StatisticsResponse):
            return (
                f"<b>Ваша статистика за {text_period}</b>:\n\n"
                f"Количество поступлений на счет: {response.income_count}\n"
                f"Общая сумма поступлений: {response.income_balance}\n"
                f"Количество списаний со счета: {response.expense_count}\n"
                f"Общая сумма списаний: {response.expense_balance}\n"
            )

        @self.router.message(lambda message: message.text == "Статистика")
        async def handle_main_statistics_button(message: types.Message):
            await message.answer(
                "Выберите тип аналитики:",
                reply_markup=Keyboards.get_all_statistics_buttons(),
            )

        @self.router.callback_query(
            F.data.in_(["per_day", "per_week", "per_month", "per_year"])
        )
        async def handle_statistics_per_period(callback: types.CallbackQuery):
            await callback.answer()

            period_type = callback_to_period[callback.data]
            rus_period = period_to_rus_period[period_type]

            statistics_dto = StatisticsRequest(
                user_id=callback.from_user.id, period=period_type
            )
            response = await self.analytic_use_case.execute(statistics_dto)
            await callback.message.answer(
                _stats_output(text_period=rus_period, response=response),
                parse_mode="HTML",
            )
