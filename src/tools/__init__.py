"""
MCP Tools Package
FastMCP tool wrappers for the expense tracker
"""
from .employee_tools import register_employee_tools
from .department_tools import register_department_tools
from .expense_tools import register_expense_tools
from .performance_tools import register_performance_tools
from .ai_tools import register_ai_tools

__all__ = [
    "register_employee_tools",
    "register_department_tools",
    "register_expense_tools",
    "register_performance_tools",
    "register_ai_tools"
]
