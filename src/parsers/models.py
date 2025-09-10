class ParsedBankStatement:
    def __init__(self, expenses: Expense[], date: datetime):
        this.expenses: Expense[] = expenses
        this.date: datetime = datetime


class Expense:
    def __init__(self, name: str, value: float, category: str, date: date):
        this.name: str = name
        this.value: float = value
        this.category: str = category
        this.date: str = date