"""
Database Viewer and Calculator
Interactive tool to view and analyze company database
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Database path
SCRIPT_DIR = Path(__file__).parent.absolute()
DB_PATH = SCRIPT_DIR / "data" / "company.db"


def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_table(headers: List[str], rows: List[tuple], max_width: int = 20):
    """Print data in table format."""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Limit max width
    col_widths = [min(w, max_width) for w in col_widths]
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell)[:col_widths[i]].ljust(col_widths[i]) 
                              for i, cell in enumerate(row))
        print(row_line)


def view_overview():
    """Display database overview."""
    print_header("DATABASE OVERVIEW")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM employees")
    emp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM expenses")
    exp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM performance")
    perf_count = cursor.fetchone()[0]
    
    # Calculate totals
    cursor.execute("SELECT SUM(salary) FROM employees")
    total_salary = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT AVG(rating) FROM performance")
    avg_rating = cursor.fetchone()[0] or 0
    
    conn.close()
    
    print(f"\n📊 Record Counts:")
    print(f"   Departments:         {dept_count:,}")
    print(f"   Employees:           {emp_count:,}")
    print(f"   Expense Records:     {exp_count:,}")
    print(f"   Performance Ratings: {perf_count:,}")
    
    print(f"\n💰 Financial Summary:")
    print(f"   Total Salary Burden: ${total_salary:,.2f}")
    print(f"   Total Expenses:      ${total_expenses:,.2f}")
    print(f"   Combined:            ${total_salary + total_expenses:,.2f}")
    
    print(f"\n⭐ Performance:")
    print(f"   Average Rating:      {avg_rating:.2f}/5.0")


def view_departments():
    """Display all departments."""
    print_header("DEPARTMENTS")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            d.name,
            d.description,
            COUNT(e.id) as emp_count,
            COALESCE(SUM(e.salary), 0) as total_salary
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name, d.description
        ORDER BY d.name
    """)
    
    departments = cursor.fetchall()
    conn.close()
    
    if not departments:
        print("\n❌ No departments found")
        return
    
    print(f"\n📁 Total Departments: {len(departments)}\n")
    for dept in departments:
        name, desc, emp_count, salary = dept
        print(f"🏢 {name}")
        print(f"   Description: {desc}")
        print(f"   Employees:   {emp_count}")
        print(f"   Salary:      ${salary:,.2f}")
        print()


def view_employees(department: str = None):
    """Display employees, optionally filtered by department."""
    if department:
        print_header(f"EMPLOYEES - {department.upper()} DEPARTMENT")
    else:
        print_header("ALL EMPLOYEES")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if department:
        cursor.execute("""
            SELECT 
                e.name,
                e.role,
                d.name as department,
                e.salary,
                e.join_date,
                COALESCE(AVG(p.rating), 0) as avg_rating
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            LEFT JOIN performance p ON e.id = p.employee_id
            WHERE LOWER(d.name) = LOWER(?)
            GROUP BY e.id, e.name, e.role, d.name, e.salary, e.join_date
            ORDER BY e.name
        """, (department,))
    else:
        cursor.execute("""
            SELECT 
                e.name,
                e.role,
                d.name as department,
                e.salary,
                e.join_date,
                COALESCE(AVG(p.rating), 0) as avg_rating
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            LEFT JOIN performance p ON e.id = p.employee_id
            GROUP BY e.id, e.name, e.role, d.name, e.salary, e.join_date
            ORDER BY d.name, e.name
        """)
    
    employees = cursor.fetchall()
    conn.close()
    
    if not employees:
        print("\n❌ No employees found")
        return
    
    print(f"\n👥 Total Employees: {len(employees)}\n")
    headers = ["Name", "Role", "Department", "Salary", "Join Date", "Avg Rating"]
    rows = [(name, role, dept, f"${salary:,.0f}", join_date, f"{rating:.1f}" if rating > 0 else "N/A")
            for name, role, dept, salary, join_date, rating in employees]
    print_table(headers, rows)
    
    # Calculate totals
    total_salary = sum(emp[3] for emp in employees)
    avg_rating = sum(emp[5] for emp in employees if emp[5] > 0) / len([e for e in employees if e[5] > 0]) if any(emp[5] > 0 for emp in employees) else 0
    
    print(f"\n💰 Total Salary: ${total_salary:,.2f}")
    if avg_rating > 0:
        print(f"⭐ Average Rating: {avg_rating:.2f}/5.0")


def view_expenses(department: str = None, days: int = 30):
    """Display expenses, optionally filtered by department and date range."""
    if department:
        print_header(f"EXPENSES - {department.upper()} DEPARTMENT (Last {days} days)")
    else:
        print_header(f"ALL EXPENSES (Last {days} days)")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    if department:
        cursor.execute("""
            SELECT 
                e.date,
                e.amount,
                e.category,
                e.note,
                d.name as department
            FROM expenses e
            JOIN departments d ON e.department_id = d.id
            WHERE LOWER(d.name) = LOWER(?) AND e.date >= ?
            ORDER BY e.date DESC
        """, (department, cutoff_date))
    else:
        cursor.execute("""
            SELECT 
                e.date,
                e.amount,
                e.category,
                e.note,
                d.name as department
            FROM expenses e
            JOIN departments d ON e.department_id = d.id
            WHERE e.date >= ?
            ORDER BY e.date DESC
        """, (cutoff_date,))
    
    expenses = cursor.fetchall()
    conn.close()
    
    if not expenses:
        print("\n❌ No expenses found")
        return
    
    print(f"\n💳 Total Expense Records: {len(expenses)}\n")
    headers = ["Date", "Amount", "Category", "Note", "Department"]
    rows = [(date, f"${amount:,.2f}", category, note[:30], dept)
            for date, amount, category, note, dept in expenses]
    print_table(headers, rows)
    
    # Calculate totals by category
    category_totals = {}
    for exp in expenses:
        category = exp[2]
        amount = exp[1]
        category_totals[category] = category_totals.get(category, 0) + amount
    
    total = sum(category_totals.values())
    
    print(f"\n📊 Expense Breakdown:")
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total * 100) if total > 0 else 0
        print(f"   {category:.<30} ${amount:>10,.2f} ({percentage:>5.1f}%)")
    
    print(f"\n💰 Total Expenses: ${total:,.2f}")


def view_performance():
    """Display performance ratings."""
    print_header("PERFORMANCE RATINGS")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            e.name,
            d.name as department,
            p.rating,
            p.month,
            p.comments
        FROM performance p
        JOIN employees e ON p.employee_id = e.id
        JOIN departments d ON e.department_id = d.id
        ORDER BY p.month DESC, d.name, e.name
    """)
    
    ratings = cursor.fetchall()
    conn.close()
    
    if not ratings:
        print("\n❌ No performance ratings found")
        return
    
    print(f"\n⭐ Total Ratings: {len(ratings)}\n")
    headers = ["Employee", "Department", "Rating", "Month", "Comments"]
    rows = [(name, dept, f"{rating}/5", month, comments[:30] if comments else "")
            for name, dept, rating, month, comments in ratings]
    print_table(headers, rows)
    
    # Calculate statistics
    avg_rating = sum(r[2] for r in ratings) / len(ratings)
    rating_counts = {}
    for r in ratings:
        rating_counts[r[2]] = rating_counts.get(r[2], 0) + 1
    
    print(f"\n📊 Rating Statistics:")
    print(f"   Average Rating: {avg_rating:.2f}/5.0")
    print(f"\n   Distribution:")
    for rating in sorted(rating_counts.keys(), reverse=True):
        count = rating_counts[rating]
        percentage = (count / len(ratings) * 100)
        bar = "█" * int(percentage / 2)
        print(f"   {rating}⭐: {bar} {count} ({percentage:.1f}%)")


def calculate_department_stats(department: str):
    """Calculate comprehensive statistics for a department."""
    print_header(f"DEPARTMENT STATISTICS - {department.upper()}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Department info
    cursor.execute("""
        SELECT id, name, description
        FROM departments
        WHERE LOWER(name) = LOWER(?)
    """, (department,))
    
    dept_info = cursor.fetchone()
    if not dept_info:
        print(f"\n❌ Department '{department}' not found")
        conn.close()
        return
    
    dept_id, dept_name, dept_desc = dept_info
    
    # Employee stats
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            COALESCE(SUM(salary), 0) as total_salary,
            COALESCE(AVG(salary), 0) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary
        FROM employees
        WHERE department_id = ?
    """, (dept_id,))
    emp_stats = cursor.fetchone()
    
    # Expense stats (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            COALESCE(SUM(amount), 0) as total,
            COALESCE(AVG(amount), 0) as avg
        FROM expenses
        WHERE department_id = ? AND date >= ?
    """, (dept_id, thirty_days_ago))
    exp_stats = cursor.fetchone()
    
    # Expense by category
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE department_id = ? AND date >= ?
        GROUP BY category
        ORDER BY total DESC
    """, (dept_id, thirty_days_ago))
    exp_categories = cursor.fetchall()
    
    # Performance stats
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            COALESCE(AVG(rating), 0) as avg_rating,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating
        FROM performance p
        JOIN employees e ON p.employee_id = e.id
        WHERE e.department_id = ?
    """, (dept_id,))
    perf_stats = cursor.fetchone()
    
    conn.close()
    
    # Print results
    print(f"\n🏢 Department: {dept_name}")
    print(f"   {dept_desc}")
    
    print(f"\n👥 EMPLOYEE STATISTICS:")
    print(f"   Total Employees:    {emp_stats[0]:,}")
    print(f"   Total Salary:       ${emp_stats[1]:,.2f}")
    print(f"   Average Salary:     ${emp_stats[2]:,.2f}")
    print(f"   Salary Range:       ${emp_stats[3]:,.2f} - ${emp_stats[4]:,.2f}")
    
    print(f"\n💳 EXPENSE STATISTICS (Last 30 days):")
    print(f"   Total Expenses:     ${exp_stats[1]:,.2f}")
    print(f"   Expense Records:    {exp_stats[0]:,}")
    print(f"   Average Expense:    ${exp_stats[2]:,.2f}")
    
    if exp_categories:
        print(f"\n   Breakdown by Category:")
        for category, total in exp_categories:
            percentage = (total / exp_stats[1] * 100) if exp_stats[1] > 0 else 0
            print(f"     {category:.<25} ${total:>10,.2f} ({percentage:>5.1f}%)")
    
    print(f"\n⭐ PERFORMANCE STATISTICS:")
    if perf_stats[0] > 0:
        print(f"   Total Ratings:      {perf_stats[0]:,}")
        print(f"   Average Rating:     {perf_stats[1]:.2f}/5.0")
        print(f"   Rating Range:       {perf_stats[2]}/5 - {perf_stats[3]}/5")
    else:
        print(f"   No performance ratings recorded")
    
    # Calculate monthly burn rate
    monthly_burn = emp_stats[1] / 12 + exp_stats[1]
    print(f"\n💰 FINANCIAL PROJECTION:")
    print(f"   Monthly Salary:     ${emp_stats[1]/12:,.2f}")
    print(f"   Monthly Expenses:   ${exp_stats[1]:,.2f}")
    print(f"   Monthly Burn Rate:  ${monthly_burn:,.2f}")
    print(f"   Annual Projection:  ${monthly_burn * 12:,.2f}")


def compare_departments():
    """Compare all departments side by side."""
    print_header("DEPARTMENT COMPARISON")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            d.name,
            COUNT(DISTINCT e.id) as emp_count,
            COALESCE(SUM(e.salary), 0) as total_salary,
            COUNT(DISTINCT ex.id) as expense_count,
            COALESCE(SUM(ex.amount), 0) as total_expenses,
            COALESCE(AVG(p.rating), 0) as avg_rating
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        LEFT JOIN expenses ex ON d.id = ex.department_id
        LEFT JOIN performance p ON e.id = p.employee_id
        GROUP BY d.id, d.name
        ORDER BY d.name
    """)
    
    departments = cursor.fetchall()
    conn.close()
    
    if not departments:
        print("\n❌ No departments found")
        return
    
    print(f"\n📊 Comparing {len(departments)} Departments:\n")
    
    headers = ["Department", "Employees", "Total Salary", "Expenses", "Total Exp", "Avg Rating"]
    rows = []
    
    for dept in departments:
        name, emp_count, salary, exp_count, expenses, rating = dept
        rows.append((
            name,
            f"{emp_count}",
            f"${salary:,.0f}",
            f"{exp_count}",
            f"${expenses:,.0f}",
            f"{rating:.1f}" if rating > 0 else "N/A"
        ))
    
    print_table(headers, rows, max_width=15)
    
    # Calculate totals
    total_employees = sum(d[1] for d in departments)
    total_salary = sum(d[2] for d in departments)
    total_expenses = sum(d[4] for d in departments)
    
    print(f"\n🏢 COMPANY TOTALS:")
    print(f"   Total Employees:    {total_employees:,}")
    print(f"   Total Salary:       ${total_salary:,.2f}")
    print(f"   Total Expenses:     ${total_expenses:,.2f}")
    print(f"   Combined Burn:      ${total_salary + total_expenses:,.2f}")


def interactive_menu():
    """Display interactive menu."""
    while True:
        print("\n" + "=" * 70)
        print("  COMPANY DATABASE VIEWER & CALCULATOR")
        print("=" * 70)
        print("\n📊 Main Menu:")
        print("   1. Database Overview")
        print("   2. View Departments")
        print("   3. View All Employees")
        print("   4. View Employees by Department")
        print("   5. View All Expenses")
        print("   6. View Expenses by Department")
        print("   7. View Performance Ratings")
        print("   8. Calculate Department Statistics")
        print("   9. Compare All Departments")
        print("   0. Exit")
        
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            view_overview()
        elif choice == "2":
            view_departments()
        elif choice == "3":
            view_employees()
        elif choice == "4":
            dept = input("Enter department name (Admin/HR/Tech/BPO): ").strip()
            view_employees(dept)
        elif choice == "5":
            view_expenses()
        elif choice == "6":
            dept = input("Enter department name (Admin/HR/Tech/BPO): ").strip()
            days = input("Enter number of days (default 30): ").strip()
            days = int(days) if days else 30
            view_expenses(dept, days)
        elif choice == "7":
            view_performance()
        elif choice == "8":
            dept = input("Enter department name (Admin/HR/Tech/BPO): ").strip()
            calculate_department_stats(dept)
        elif choice == "9":
            compare_departments()
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        if not DB_PATH.exists():
            print(f"\n❌ Database not found at: {DB_PATH}")
            print("   Please run populate_data.py first to create sample data.")
        else:
            interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
