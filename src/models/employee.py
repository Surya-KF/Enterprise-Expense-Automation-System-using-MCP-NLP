"""
Employee Model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    """Employee data model"""
    name: str
    role: str
    department_id: int
    salary: float
    employee_number: Optional[str] = None
    join_date: Optional[str] = None
    id: Optional[int] = None
