"""
Database Schema Module
Handles database initialization and schema creation
"""
import json
import sqlite3
from src.config import DB_PATH, DEPARTMENTS_JSON


def init_database():
    """Initialize SQLite database with required tables and indexes."""
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
