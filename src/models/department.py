"""
Department Model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Department:
    """Department data model"""
    name: str
    description: str = ""
    id: Optional[int] = None
