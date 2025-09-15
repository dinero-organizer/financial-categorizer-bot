from datetime import datetime, date
from typing import List


class Expense:
    def __init__(self, name: str, value: float, category: str, date: date):
        self.name: str = name
        self.value: float = value
        self.category: str = category
        self.date: date = date


class ParsedBankStatement:
    def __init__(self, expenses: List[Expense], date: datetime):
        self.expenses: List[Expense] = expenses
        self.date: datetime = date