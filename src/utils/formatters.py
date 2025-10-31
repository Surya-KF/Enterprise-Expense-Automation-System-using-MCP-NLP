"""
Formatter Functions
"""
from datetime import datetime


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_date(date_obj: datetime) -> str:
    """
    Format datetime object as YYYY-MM-DD string.
    
    Args:
        date_obj: Datetime object to format
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime("%Y-%m-%d")
