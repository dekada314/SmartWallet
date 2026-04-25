class GettingUserError(Exception):
    """Такого пользователя не существует"""


class NotValidAmountError(Exception):
    """Введенное значение нельзя интерпретировать как число"""
