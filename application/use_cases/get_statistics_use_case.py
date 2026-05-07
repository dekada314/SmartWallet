from datetime import datetime, timedelta

from app.core.logs_config.logger_wrappers import use_case_logger
from app.dto.requests.get_statistics_request import StatisticsRequest
from app.dto.responses.statistics_reponse import StatisticsResponse
from application.use_cases.enums import PeriodType
from domain.entities.transaction import Transaction, TransactionType
from domain.repositories.base_transaction_repository import BaseTransactionRepository


class GetStatiscticsPerPeriod:
    def __init__(self, transaction_repo: BaseTransactionRepository):
        self.transaction_repo = transaction_repo

    @use_case_logger
    async def execute(self, statistics_dto: StatisticsRequest) -> StatisticsResponse:
        now = datetime.now()

        match statistics_dto.period:
            case PeriodType.DAY:
                start_date = now - timedelta(days=1)

            case PeriodType.WEEK:
                start_date = now - timedelta(days=7)

            case PeriodType.MONTH:
                start_date = now - timedelta(days=30)

            case PeriodType.YEAR:
                start_date = now - timedelta(days=365)

            case _:
                raise ValueError

        transactions: list[
            Transaction
        ] = await self.transaction_repo.get_transactions_by_period(
            statistics_dto.user_id, start_date, now
        )
        income_transactions = list(
            filter(
                lambda transaction: transaction.transaction_type
                == TransactionType.INCOME.value,
                transactions,
            )
        )
        income_balance = sum([tr.amount for tr in income_transactions])

        expense_transactions = list(
            filter(
                lambda transaction: transaction.transaction_type
                == TransactionType.EXPENSE.value,
                transactions,
            )
        )

        expense_balance = sum([tr.amount for tr in expense_transactions])

        return StatisticsResponse(
            income_balance=income_balance,
            income_count=len(income_transactions),
            expense_balance=expense_balance,
            expense_count=len(expense_transactions),
        )
