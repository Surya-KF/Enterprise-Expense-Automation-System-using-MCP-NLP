"""
Performance Model
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Performance:
    """Performance rating data model"""
    employee_id: int
    rating: int
    month: Optional[str] = None
    comments: str = ""
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validate rating"""
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
