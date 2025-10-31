"""
Validator Functions
"""
from datetime import datetime


def validate_rating(rating: int) -> bool:
    """
    Validate performance rating is between 1 and 5.
    
    Args:
        rating: Rating value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= rating <= 5


def validate_date_format(date_string: str) -> bool:
    """
    Validate date string is in YYYY-MM-DD format.
    
    Args:
        date_string: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False
