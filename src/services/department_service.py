"""
Department Service Module
Business logic for department operations
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any

from src.database.connection import get_db_connection
from src.database.queries import get_department_id


class DepartmentService:
    """Service for department-related operations"""
    
    @staticmethod
    async def add_department(name: str, description: str = "") -> Dict[str, Any]:
        """
        Add a new department to the system.
        
        Args:
            name: Department name (must be unique)
            description: Department description
            
        Returns:
            Operation result dictionary
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO departments (name, description) VALUES (?, ?)",
                (name, description)
            )
            dept_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Department '{name}' added successfully",
                "department_id": dept_id
            }
        except sqlite3.IntegrityError:
            return {
                "status": "error",
                "message": f"Department '{name}' already exists"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding department: {str(e)}"
            }
    
    @staticmethod
    async def delete_department(department_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a department. Use force=True to delete even if it has employees/expenses.
        
        Args:
            department_name: Name of the department to delete
            force: If True, cascade delete all associated records
            
        Returns:
            Deletion result with cascade information
        """
        try:
            dept_id = get_department_id(department_name)
            if not dept_id:
                return {
                    "status": "error",
                    "message": f"Department '{department_name}' not found"
                }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check for associated records
            cursor.execute("SELECT COUNT(*) FROM employees WHERE department_id = ?", (dept_id,))
            emp_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM expenses WHERE department_id = ?", (dept_id,))
            exp_count = cursor.fetchone()[0]
            
            if (emp_count > 0 or exp_count > 0) and not force:
                conn.close()
                return {
                    "status": "error",
                    "message": f"Cannot delete department '{department_name}': it has {emp_count} employees and {exp_count} expenses. Use force=True to delete anyway.",
                    "employees_count": emp_count,
                    "expenses_count": exp_count
                }
            
            # If force=True, delete associated records first
            perf_deleted = 0
            if force:
                # Delete performance records for employees in this department
                cursor.execute("""
                    DELETE FROM performance 
                    WHERE employee_id IN (SELECT id FROM employees WHERE department_id = ?)
                """, (dept_id,))
                perf_deleted = cursor.rowcount
                
                # Delete employees
                cursor.execute("DELETE FROM employees WHERE department_id = ?", (dept_id,))
                
                # Delete expenses
                cursor.execute("DELETE FROM expenses WHERE department_id = ?", (dept_id,))
            
            # Delete the department
            cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
            
            conn.commit()
            conn.close()
            
            result = {
                "status": "success",
                "message": f"Department '{department_name}' deleted successfully",
                "deleted_department": department_name
            }
            
            if force:
                result["cascade_deleted"] = {
                    "employees": emp_count,
                    "expenses": exp_count,
                    "performance_records": perf_deleted
                }
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting department: {str(e)}"
            }
    
    @staticmethod
    async def get_department_summary(department_name: str) -> Dict[str, Any]:
        """
        Get comprehensive summary for a specific department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            Comprehensive department analytics
        """
        try:
            dept_id = get_department_id(department_name)
            if not dept_id:
                return {
                    "status": "error",
                    "message": f"Department '{department_name}' not found"
                }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get department info
            cursor.execute("SELECT * FROM departments WHERE id = ?", (dept_id,))
            dept_info = dict(cursor.fetchone())
            
            # Employee count and total salary
            cursor.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(salary), 0) as total_salary
                FROM employees WHERE department_id = ?
            """, (dept_id,))
            emp_stats = dict(cursor.fetchone())
            
            # Recent expenses (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM expenses
                WHERE department_id = ? AND date >= ?
            """, (dept_id, thirty_days_ago))
            expense_stats = dict(cursor.fetchone())
            
            # Expense by category
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE department_id = ? AND date >= ?
                GROUP BY category
                ORDER BY total DESC
            """, (dept_id, thirty_days_ago))
            expense_by_category = [dict(row) for row in cursor.fetchall()]
            
            # Average performance rating (last 3 months)
            three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m")
            cursor.execute("""
                SELECT AVG(p.rating) as avg_rating, COUNT(p.id) as rating_count
                FROM performance p
                JOIN employees e ON p.employee_id = e.id
                WHERE e.department_id = ? AND p.month >= ?
            """, (dept_id, three_months_ago))
            perf_stats = dict(cursor.fetchone())
            
            conn.close()
            
            return {
                "status": "success",
                "department": dept_info,
                "employees": {
                    "count": emp_stats["count"],
                    "total_salary_burden": round(emp_stats["total_salary"], 2)
                },
                "expenses_last_30_days": {
                    "total": round(expense_stats["total"], 2),
                    "count": expense_stats["count"],
                    "by_category": expense_by_category
                },
                "performance_last_3_months": {
                    "average_rating": round(perf_stats["avg_rating"], 2) if perf_stats["avg_rating"] else 0,
                    "rating_count": perf_stats["rating_count"]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting department summary: {str(e)}"
            }
