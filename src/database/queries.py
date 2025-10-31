"""
Database Query Helpers
Common database queries and helper functions
"""
from typing import Optional
from src.database.connection import get_db_connection


def get_department_id(department_name: str) -> Optional[int]:
    """
    Get department ID by name.
    
    Args:
        department_name: Name of the department
        
    Returns:
        Department ID or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM departments WHERE LOWER(name) = LOWER(?)", (department_name,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None


def get_employee_id(employee_name: str) -> Optional[int]:
    """
    Get employee ID by name.
    
    Args:
        employee_name: Name of the employee
        
    Returns:
        Employee ID or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees WHERE LOWER(name) = LOWER(?)", (employee_name,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None


def generate_employee_number() -> str:
    """
    Generate a unique employee number.
    
    Returns:
        Employee number in format EMP0001, EMP0002, etc.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    conn.close()
    return f"EMP{count + 1:04d}"
