from dataclasses import dataclass
from datetime import date
import time


@dataclass
class Expense:
    id: str
    category: str
    date: date
    amount: int
    tax: int
    payment: str
    note: str
