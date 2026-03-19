from repository.base_goals_repository import BaseGoalsRepository


class NotificationUseCase:
    def __init__(self, notification_repository: BaseGoalsRepository):
        self.notification_repository = notification_repository

    async def execute(self, user_id: int):
        goals = self.notification_repository.get_all_user_goals(user_id)
