"""
Expense Service Module
Business logic for expense operations
"""
from datetime import datetime
from typing import Dict, Any, Optional

from src.database.connection import get_db_connection
from src.database.queries import get_department_id


class ExpenseService:
    """Service for expense-related operations"""
    
    @staticmethod
    async def add_expense(
        amount: float,
        category: str,
        department_name: str,
        date: Optional[str] = None,
        note: str = ""
    ) -> Dict[str, Any]:
        """
        Add a new expense record.
        
        Args:
            amount: Expense amount
            category: Expense category
            department_name: Department name
            date: Expense date (defaults to today)
            note: Optional note
            
        Returns:
            Operation result dictionary
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            dept_id = get_department_id(department_name)
            if not dept_id:
                return {
                    "status": "error",
                    "message": f"Department '{department_name}' not found"
                }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (date, amount, category, note, department_id) VALUES (?, ?, ?, ?, ?)",
                (date, amount, category, note, dept_id)
            )
            expense_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Expense added successfully to {department_name}",
                "expense_id": expense_id,
                "amount": amount,
                "category": category
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding expense: {str(e)}"
            }
    
    @staticmethod
    async def list_expenses(
        department_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List expenses with optional filters.
        
        Args:
            department_name: Optional department filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of expenses with analytics
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT e.id, e.date, e.amount, e.category, e.note, d.name as department
                FROM expenses e
                JOIN departments d ON e.department_id = d.id
                WHERE 1=1
            """
            params = []
            
            if department_name:
                dept_id = get_department_id(department_name)
                if not dept_id:
                    return {
                        "status": "error",
                        "message": f"Department '{department_name}' not found"
                    }
                query += " AND e.department_id = ?"
                params.append(dept_id)
            
            if start_date:
                query += " AND e.date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND e.date <= ?"
                params.append(end_date)
            
            query += " ORDER BY e.date DESC"
            
            cursor.execute(query, params)
            expenses = [dict(row) for row in cursor.fetchall()]
            
            total = sum(exp["amount"] for exp in expenses)
            
            # Category breakdown
            categories = {}
            for exp in expenses:
                cat = exp["category"]
                categories[cat] = categories.get(cat, 0) + exp["amount"]
            
            conn.close()
            
            return {
                "status": "success",
                "count": len(expenses),
                "total_amount": round(total, 2),
                "department": department_name or "All",
                "date_range": {
                    "start": start_date or "Beginning",
                    "end": end_date or "Present"
                },
                "category_breakdown": categories,
                "expenses": expenses
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error listing expenses: {str(e)}"
            }
    
    @staticmethod
    async def delete_expense(expense_id: int) -> Dict[str, Any]:
        """
        Delete an expense record by ID.
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            Deletion result
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get expense details before deleting
            cursor.execute("""
                SELECT e.id, e.date, e.amount, e.category, e.note, d.name as department
                FROM expenses e
                JOIN departments d ON e.department_id = d.id
                WHERE e.id = ?
            """, (expense_id,))
            
            expense = cursor.fetchone()
            if not expense:
                conn.close()
                return {
                    "status": "error",
                    "message": f"Expense ID {expense_id} not found"
                }
            
            exp_id, date, amount, category, note, dept = expense
            
            # Delete the expense
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Expense deleted successfully",
                "deleted_expense": {
                    "id": exp_id,
                    "date": date,
                    "amount": amount,
                    "category": category,
                    "department": dept,
                    "note": note
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting expense: {str(e)}"
            }
