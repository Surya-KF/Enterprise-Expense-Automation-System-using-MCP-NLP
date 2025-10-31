"""
Performance Service Module
Business logic for performance rating operations
"""
from datetime import datetime
from typing import Dict, Any, Optional

from src.database.connection import get_db_connection
from src.database.queries import get_employee_id


class PerformanceService:
    """Service for performance rating operations"""
    
    @staticmethod
    async def add_performance(
        employee_name: str,
        rating: int,
        month: Optional[str] = None,
        comments: str = ""
    ) -> Dict[str, Any]:
        """
        Add a performance rating for an employee.
        
        Args:
            employee_name: Employee name
            rating: Performance rating (1-5)
            month: Month for the rating (defaults to current month)
            comments: Optional comments
            
        Returns:
            Operation result dictionary
        """
        try:
            if not 1 <= rating <= 5:
                return {
                    "status": "error",
                    "message": "Rating must be between 1 and 5"
                }
            
            if month is None:
                month = datetime.now().strftime("%Y-%m")
            
            emp_id = get_employee_id(employee_name)
            if not emp_id:
                return {
                    "status": "error",
                    "message": f"Employee '{employee_name}' not found"
                }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO performance (employee_id, rating, month, comments) VALUES (?, ?, ?, ?)",
                (emp_id, rating, month, comments)
            )
            perf_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Performance rating added for '{employee_name}'",
                "performance_id": perf_id,
                "rating": rating,
                "month": month
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding performance: {str(e)}"
            }
