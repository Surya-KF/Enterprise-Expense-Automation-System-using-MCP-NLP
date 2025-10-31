"""
Database Connection Module
Handles SQLite database connections
"""
import sqlite3
from src.config import DB_PATH


def get_db_connection():
    """
    Get a database connection with Row factory.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
