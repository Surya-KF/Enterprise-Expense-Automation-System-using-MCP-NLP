"""
Expense MCP Tools
Tool wrappers for expense operations
"""
import json
from fastmcp import FastMCP

from src.services.expense_service import ExpenseService


def register_expense_tools(mcp: FastMCP):
    """Register expense-related MCP tools"""
    
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
        result = await ExpenseService.add_expense(amount, category, department_name, date, note)
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
        result = await ExpenseService.list_expenses(department_name, start_date, end_date)
        return json.dumps(result, indent=2)
    
    @mcp.tool(name="delete_expense")
    async def delete_expense_tool(expense_id: int) -> str:
        """
        Delete an expense record. Use when user says 'remove expense', 'delete expense', or 'wrong expense entry'.
        
        Args:
            expense_id: The ID of the expense to delete (use list_expenses to find IDs)
        """
        result = await ExpenseService.delete_expense(expense_id)
        return json.dumps(result, indent=2)
