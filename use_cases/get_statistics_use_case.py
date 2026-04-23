from datetime import datetime, timedelta

from domain.entities.transaction import Transaction, TransactionType
from handlers.requests.statistics_request import StatisticsRequest
from repository.base_transaction_repository import BaseTransactionRepository
from use_cases.enums import PeriodType
from use_cases.statistics_reponse import StatisticsResponse


class GetStatiscticsPerPeriod:
    def __init__(self, transaction_repo: BaseTransactionRepository):
        self.transaction_repo = transaction_repo

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

        transactions = await self.transaction_repo.get_transactions_by_period(
            statistics_dto.user_id, start_date, now
        )

        income_transactions = filter(
            lambda transaction: transaction.transaction_type == TransactionType.INCOME,
            transactions,
        )
        income_balance = sum(income_transactions)

        expense_balance = sum(
            filter(
                lambda transaction: transaction.transaction_type
                == TransactionType.EXPENSE,
                transactions,
            )
        )

        return StatisticsResponse(
            income_balance=income_balance,
            income_count=len(income_transactions),
            expense_balance=expense_balance,
            expense_count=len(transactions) - len(income_transactions),
        )
