"""
Expense Model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Expense:
    """Expense data model"""
    amount: float
    category: str
    department_id: int
    date: Optional[str] = None
    note: str = ""
    id: Optional[int] = None
