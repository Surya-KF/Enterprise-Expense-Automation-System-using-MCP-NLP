"""
Employee Service Module
Business logic for employee operations
"""
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

from src.database.connection import get_db_connection
from src.database.queries import get_department_id, generate_employee_number


class EmployeeService:
    """Service for employee-related operations"""
    
    @staticmethod
    async def add_employee(
        name: str,
        role: str,
        department_name: str,
        salary: float,
        employee_number: Optional[str] = None,
        join_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new employee to the system.
        
        Args:
            name: Employee full name
            role: Job role/title
            department_name: Department name
            salary: Annual salary
            employee_number: Unique employee ID (auto-generated if not provided)
            join_date: Join date (defaults to today)
            
        Returns:
            Operation result dictionary
        """
        try:
            dept_id = get_department_id(department_name)
            if not dept_id:
                return {
                    "status": "error",
                    "message": f"Department '{department_name}' not found"
                }
            
            if join_date is None:
                join_date = datetime.now().strftime("%Y-%m-%d")
            
            if employee_number is None:
                employee_number = generate_employee_number()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO employees (employee_number, name, role, department_id, salary, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                (employee_number, name, role, dept_id, salary, join_date)
            )
            emp_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Employee '{name}' (#{employee_number}) added successfully to {department_name}",
                "employee_id": emp_id,
                "employee_number": employee_number
            }
        except sqlite3.IntegrityError as e:
            if "employee_number" in str(e):
                return {
                    "status": "error",
                    "message": f"Employee number '{employee_number}' already exists"
                }
            return {
                "status": "error",
                "message": f"Error adding employee: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding employee: {str(e)}"
            }
    
    @staticmethod
    async def list_employees(department_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List all employees, optionally filtered by department.
        
        Args:
            department_name: Optional department filter
            
        Returns:
            List of employees with metadata
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if department_name:
                dept_id = get_department_id(department_name)
                if not dept_id:
                    return {
                        "status": "error",
                        "message": f"Department '{department_name}' not found"
                    }
                
                cursor.execute("""
                    SELECT e.id, e.employee_number, e.name, e.role, d.name as department, e.salary, e.join_date
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                    WHERE e.department_id = ?
                    ORDER BY e.name
                """, (dept_id,))
            else:
                cursor.execute("""
                    SELECT e.id, e.employee_number, e.name, e.role, d.name as department, e.salary, e.join_date
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                    ORDER BY d.name, e.name
                """)
            
            employees = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                "status": "success",
                "count": len(employees),
                "department": department_name or "All",
                "employees": employees
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error listing employees: {str(e)}"
            }
    
    @staticmethod
    async def delete_employee(employee_identifier: str) -> Dict[str, Any]:
        """
        Delete an employee by employee_number or name.
        
        Args:
            employee_identifier: Employee number or name
            
        Returns:
            Deletion result with cascade information
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Try to find by employee_number first, then by name
            cursor.execute("""
                SELECT id, employee_number, name, role, department_id 
                FROM employees 
                WHERE employee_number = ? OR LOWER(name) = LOWER(?)
            """, (employee_identifier, employee_identifier))
            
            employee = cursor.fetchone()
            if not employee:
                conn.close()
                return {
                    "status": "error",
                    "message": f"Employee '{employee_identifier}' not found"
                }
            
            emp_id, emp_num, emp_name, role, dept_id = employee
            
            # Check for associated performance records
            cursor.execute("SELECT COUNT(*) FROM performance WHERE employee_id = ?", (emp_id,))
            perf_count = cursor.fetchone()[0]
            
            # Delete associated performance records first (cascade delete)
            if perf_count > 0:
                cursor.execute("DELETE FROM performance WHERE employee_id = ?", (emp_id,))
            
            # Delete the employee
            cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Employee '{emp_name}' ({emp_num}) deleted successfully",
                "deleted_employee": {
                    "employee_number": emp_num,
                    "name": emp_name,
                    "role": role
                },
                "performance_records_deleted": perf_count
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting employee: {str(e)}"
            }
    
    @staticmethod
    async def delete_duplicates() -> Dict[str, Any]:
        """
        Find and delete duplicate employees (same name in same department).
        
        Returns:
            List of deleted duplicates
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Find duplicates (same name + department, keeping the oldest one)
            cursor.execute("""
                SELECT e1.id, e1.employee_number, e1.name, d.name as department, e1.join_date
                FROM employees e1
                JOIN departments d ON e1.department_id = d.id
                WHERE EXISTS (
                    SELECT 1 FROM employees e2
                    WHERE e1.name = e2.name 
                    AND e1.department_id = e2.department_id
                    AND e1.id > e2.id
                )
                ORDER BY e1.name, e1.id
            """)
            
            duplicates = cursor.fetchall()
            
            if not duplicates:
                conn.close()
                return {
                    "status": "success",
                    "message": "No duplicate employees found",
                    "duplicates_deleted": 0
                }
            
            deleted_list = []
            for dup_id, emp_num, name, dept, join_date in duplicates:
                # Delete performance records
                cursor.execute("DELETE FROM performance WHERE employee_id = ?", (dup_id,))
                
                # Delete employee
                cursor.execute("DELETE FROM employees WHERE id = ?", (dup_id,))
                
                deleted_list.append({
                    "employee_number": emp_num,
                    "name": name,
                    "department": dept,
                    "join_date": join_date
                })
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Deleted {len(duplicates)} duplicate employees",
                "duplicates_deleted": len(duplicates),
                "deleted_employees": deleted_list
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting duplicates: {str(e)}"
            }
