"""
Tech Company Management & Analytics System
Built with FastMCP, SQLite, and AI Integration (Gemini-2.5-flash)
"""

import asyncio
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import google.generativeai as genai
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration - Use absolute paths
SCRIPT_DIR = Path(__file__).parent.absolute()
DB_PATH = SCRIPT_DIR / "data" / "company.db"
DEPARTMENTS_JSON = SCRIPT_DIR / "data" / "departments.json"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

# Ensure data directory exists
DB_PATH.parent.mkdir(exist_ok=True)


# ==================== Database Initialization ====================

def init_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)
    
    # Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_number TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            salary REAL NOT NULL,
            join_date TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    """)
    
    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            department_id INTEGER NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    """)
    
    # Create performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            month TEXT NOT NULL,
            comments TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_dept ON expenses(department_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_emp ON performance(employee_id)")
    
    # Initialize departments from JSON if they don't exist
    cursor.execute("SELECT COUNT(*) as count FROM departments")
    if cursor.fetchone()[0] == 0:
        if DEPARTMENTS_JSON.exists():
            with open(DEPARTMENTS_JSON, 'r') as f:
                departments = json.load(f)
                for dept in departments:
                    cursor.execute(
                        "INSERT INTO departments (name, description) VALUES (?, ?)",
                        (dept["name"], dept["description"])
                    )
            conn.commit()
    
    conn.close()


# ==================== Database Helper Functions ====================

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_department_id(department_name: str) -> Optional[int]:
    """Get department ID by name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM departments WHERE LOWER(name) = LOWER(?)", (department_name,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None


def get_employee_id(employee_name: str) -> Optional[int]:
    """Get employee ID by name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees WHERE LOWER(name) = LOWER(?)", (employee_name,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None


# ==================== AI Integration ====================

async def call_ai_api(prompt: str) -> str:
    """
    Call the configured AI API (Gemini or Claude) with the given prompt.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_key_here":
        return "Error: GEMINI_API_KEY not configured in .env file"
            
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = await asyncio.to_thread(model.generate_content, prompt)
    return response.text



# ==================== CRUD Operations ====================

async def add_department(name: str, description: str = "") -> Dict[str, Any]:
    """Add a new department to the system."""
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


async def add_employee(
    name: str,
    role: str,
    department_name: str,
    salary: float,
    employee_number: str = None,
    join_date: str = None
) -> Dict[str, Any]:
    """Add a new employee to the system."""
    try:
        dept_id = get_department_id(department_name)
        if not dept_id:
            return {
                "status": "error",
                "message": f"Department '{department_name}' not found"
            }
        
        if join_date is None:
            join_date = datetime.now().strftime("%Y-%m-%d")
        
        # Generate employee number if not provided
        if employee_number is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            conn.close()
            # Format: EMP0001, EMP0002, etc.
            employee_number = f"EMP{count + 1:04d}"
        
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


async def add_expense(
    amount: float,
    category: str,
    department_name: str,
    date: str = None,
    note: str = ""
) -> Dict[str, Any]:
    """Add a new expense record."""
    try:
        # Default to today if no date provided
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


async def add_performance(
    employee_name: str,
    rating: int,
    month: str = None,
    comments: str = ""
) -> Dict[str, Any]:
    """Add a performance rating for an employee."""
    try:
        if not 1 <= rating <= 5:
            return {
                "status": "error",
                "message": "Rating must be between 1 and 5"
            }
        
        # Default to current month if not provided
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


# ==================== Delete Operations ====================

async def delete_employee(
    employee_identifier: str
) -> Dict[str, Any]:
    """Delete an employee by employee_number or name."""
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


async def delete_expense(
    expense_id: int
) -> Dict[str, Any]:
    """Delete an expense record by ID."""
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


async def delete_department(
    department_name: str,
    force: bool = False
) -> Dict[str, Any]:
    """Delete a department. Use force=True to delete even if it has employees/expenses."""
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
                "performance_records": perf_deleted if 'perf_deleted' in locals() else 0
            }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting department: {str(e)}"
        }


async def delete_duplicate_employees() -> Dict[str, Any]:
    """Find and delete duplicate employees (same name in same department)."""
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


# ==================== Query Operations ====================

async def list_employees(department_name: str = None) -> Dict[str, Any]:
    """List all employees, optionally filtered by department."""
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


async def list_expenses(
    department_name: str = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """List expenses with optional filters."""
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


async def get_department_summary(department_name: str) -> Dict[str, Any]:
    """Get comprehensive summary for a specific department."""
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


async def get_all_departments_summary() -> List[Dict[str, Any]]:
    """Get summary for all departments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM departments ORDER BY name")
    departments = [row["name"] for row in cursor.fetchall()]
    conn.close()
    
    summaries = []
    for dept_name in departments:
        summary = await get_department_summary(dept_name)
        if summary["status"] == "success":
            summaries.append(summary)
    
    return summaries


async def analyze_company_with_ai(query: str) -> Dict[str, Any]:
    """Analyze company data using AI (Gemini or Claude)."""
    try:
        # Gather comprehensive data
        summaries = await get_all_departments_summary()
        
        # Get overall company stats
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        total_employees = cursor.fetchone()["count"]
        
        cursor.execute("SELECT SUM(salary) as total FROM employees")
        total_salary = cursor.fetchone()["total"] or 0
        
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE date >= ?", (thirty_days_ago,))
        total_expenses_30d = cursor.fetchone()["total"] or 0
        
        conn.close()
        
        # Build AI prompt
        prompt = f"""
You are an expert company analytics assistant analyzing a tech company with 4 departments: Admin, HR, Tech, and BPO.

COMPANY OVERVIEW:
- Total Employees: {total_employees}
- Total Salary Burden: ${total_salary:,.2f}
- Total Expenses (Last 30 Days): ${total_expenses_30d:,.2f}

DEPARTMENT SUMMARIES:
{json.dumps(summaries, indent=2)}

USER QUERY: "{query}"

Please provide:
1. A direct answer to the user's question
2. Key insights and patterns you observe in the data
3. Specific recommendations based on the data
4. Any concerns or red flags worth noting

Format your response as a clear, structured analysis that is both data-driven and actionable.
"""
        
        # Call AI API
        analysis = await call_ai_api(prompt)
        
        return {
            "status": "success",
            "query": query,
            "analysis": analysis,
            "data_scope": {
                "total_employees": total_employees,
                "departments_analyzed": len(summaries),
                "expense_period": f"Last 30 days ({thirty_days_ago} to {datetime.now().strftime('%Y-%m-%d')})"
            },
            "ai_provider": AI_PROVIDER.upper()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error in AI analysis: {str(e)}"
        }


# ==================== FastMCP Server Setup ====================

# Initialize database when module loads
init_database()

# Create FastMCP server
mcp = FastMCP("company-expense-tracker")


@mcp.tool(name="add_expense")
async def add_expense_tool(
    amount: float,
    category: str,
    department_name: str,
    date: str = None,
    note: str = ""
) -> str:
    """
    Track a new expense for the tech company. Use this when user says things like 'add expense', 'record payment', 'log spending', or 'track cost'. 
    Supports natural language like 'add $500 for AWS to Tech department'.
    
    Args:
        amount: Expense amount in dollars
        category: Expense category (Infrastructure, Software Licenses, Training, Office Supplies, Utilities, Salaries, Recruitment, Events, Equipment, Maintenance)
        department_name: Department name (Admin, HR, Tech, or BPO)
        date: Expense date (YYYY-MM-DD), defaults to today if not specified
        note: Optional description or note about the expense
    """
    result = await add_expense(amount, category, department_name, date, note)
    return json.dumps(result, indent=2)


@mcp.tool(name="list_expenses")
async def list_expenses_tool(
    department_name: str = None,
    start_date: str = None,
    end_date: str = None
) -> str:
    """
    View and analyze company expenses. Use when user asks 'show expenses', 'what did we spend', 'list costs', 'expense report', or 'spending history'. 
    Supports queries like 'show me Tech expenses from last month'.
    
    Args:
        department_name: Filter by department (Admin, HR, Tech, or BPO) - optional
        start_date: Start date YYYY-MM-DD for filtering expenses - optional
        end_date: End date YYYY-MM-DD for filtering expenses - optional
    """
    result = await list_expenses(department_name, start_date, end_date)
    return json.dumps(result, indent=2)


@mcp.tool(name="get_department_summary")
async def get_department_summary_tool(department_name: str) -> str:
    """
    Get comprehensive analytics and insights for a department including employees, expenses, and performance. 
    Use when user asks 'how is Tech doing', 'department overview', 'show me HR stats', or 'department report'.
    
    Args:
        department_name: Department name (Admin, HR, Tech, or BPO)
    """
    result = await get_department_summary(department_name)
    return json.dumps(result, indent=2)


@mcp.tool(name="analyze_company_with_ai")
async def analyze_company_with_ai_tool(query: str) -> str:
    """
    Get AI-powered insights and analysis about company data. Use for complex queries like 'which department spends most', 
    'analyze trends', 'budget recommendations', 'identify issues', or any analytical question. 
    This is the MOST POWERFUL tool for natural language queries.
    
    Args:
        query: Natural language question or analysis request about the company
    """
    result = await analyze_company_with_ai(query)
    return json.dumps(result, indent=2)


@mcp.tool(name="add_employee")
async def add_employee_tool(
    name: str,
    role: str,
    department_name: str,
    salary: float,
    employee_number: str = None,
    join_date: str = None
) -> str:
    """
    Add a new employee to the company. Use when user says 'hire', 'add employee', 'new team member', or 'onboard'.
    
    Args:
        name: Employee full name
        role: Job role/title (e.g., Software Engineer, HR Manager, Office Manager)
        department_name: Department (Admin, HR, Tech, or BPO)
        salary: Annual salary in dollars
        employee_number: Unique employee ID (e.g., EMP0001). Auto-generated if not provided.
        join_date: Join date (YYYY-MM-DD, defaults to today if not specified)
    """
    result = await add_employee(name, role, department_name, salary, employee_number, join_date)
    return json.dumps(result, indent=2)


@mcp.tool(name="list_employees")
async def list_employees_tool(department_name: str = None) -> str:
    """
    List employees with optional department filter. Use when user asks 'who works here', 'show employees', 'list team', or 'who is in Tech department'.
    
    Args:
        department_name: Filter by department (Admin, HR, Tech, or BPO) - optional
    """
    result = await list_employees(department_name)
    return json.dumps(result, indent=2)


@mcp.tool(name="add_performance")
async def add_performance_tool(
    employee_name: str,
    rating: int,
    month: str = None,
    comments: str = ""
) -> str:
    """
    Add a performance rating for an employee. Use when user says 'rate employee', 'performance review', or 'add rating'.
    
    Args:
        employee_name: Employee full name
        rating: Performance rating from 1 (poor) to 5 (excellent)
        month: Month for the rating (YYYY-MM format, defaults to current month)
        comments: Optional performance comments or feedback
    """
    result = await add_performance(employee_name, rating, month, comments)
    return json.dumps(result, indent=2)


@mcp.tool(name="add_department")
async def add_department_tool(name: str, description: str = "") -> str:
    """
    Create a new department in the company. Use when user says 'add department', 'create new department', or 'new team'.
    
    Args:
        name: Department name (must be unique)
        description: Department description
    """
    result = await add_department(name, description)
    return json.dumps(result, indent=2)


@mcp.tool(name="delete_employee")
async def delete_employee_tool(employee_identifier: str) -> str:
    """
    Delete an employee from the system. Use when user says 'remove employee', 'delete employee', 'fire', or 'remove duplicate'.
    Can identify by employee_number (e.g., EMP0001) or by name.
    
    Args:
        employee_identifier: Employee number (EMP0001) or employee name
    """
    result = await delete_employee(employee_identifier)
    return json.dumps(result, indent=2)


@mcp.tool(name="delete_expense")
async def delete_expense_tool(expense_id: int) -> str:
    """
    Delete an expense record. Use when user says 'remove expense', 'delete expense', or 'wrong expense entry'.
    
    Args:
        expense_id: The ID of the expense to delete (use list_expenses to find IDs)
    """
    result = await delete_expense(expense_id)
    return json.dumps(result, indent=2)


@mcp.tool(name="delete_department")
async def delete_department_tool(department_name: str, force: bool = False) -> str:
    """
    Delete a department. Use when user says 'remove department', 'delete department', or 'close department'.
    By default, prevents deletion if department has employees/expenses. Use force=True to cascade delete.
    
    Args:
        department_name: Name of the department to delete
        force: If True, deletes department and all associated employees/expenses (default: False)
    """
    result = await delete_department(department_name, force)
    return json.dumps(result, indent=2)


@mcp.tool(name="delete_duplicate_employees")
async def delete_duplicate_employees_tool() -> str:
    """
    Find and delete duplicate employees automatically. Use when user says 'remove duplicates', 'clean up duplicates', or 'find duplicate employees'.
    Keeps the oldest record for each duplicate (earliest join_date).
    """
    result = await delete_duplicate_employees()
    return json.dumps(result, indent=2)


# This is the entry point for fastmcp
if __name__ == "__main__":
    mcp.run()
