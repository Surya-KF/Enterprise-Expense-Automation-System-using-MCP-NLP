"""
Employee MCP Tools
Tool wrappers for employee operations
"""
import json
from fastmcp import FastMCP

from src.services.employee_service import EmployeeService


def register_employee_tools(mcp: FastMCP):
    """Register employee-related MCP tools"""
    
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
        result = await EmployeeService.add_employee(name, role, department_name, salary, employee_number, join_date)
        return json.dumps(result, indent=2)
    
    @mcp.tool(name="list_employees")
    async def list_employees_tool(department_name: str = None) -> str:
        """
        List employees with optional department filter. Use when user asks 'who works here', 'show employees', 'list team', or 'who is in Tech department'.
        
        Args:
            department_name: Filter by department (Admin, HR, Tech, or BPO) - optional
        """
        result = await EmployeeService.list_employees(department_name)
        return json.dumps(result, indent=2)
    
    @mcp.tool(name="delete_employee")
    async def delete_employee_tool(employee_identifier: str) -> str:
        """
        Delete an employee from the system. Use when user says 'remove employee', 'delete employee', 'fire', or 'remove duplicate'.
        Can identify by employee_number (e.g., EMP0001) or by name.
        
        Args:
            employee_identifier: Employee number (EMP0001) or employee name
        """
        result = await EmployeeService.delete_employee(employee_identifier)
        return json.dumps(result, indent=2)
    
    @mcp.tool(name="delete_duplicate_employees")
    async def delete_duplicate_employees_tool() -> str:
        """
        Find and delete duplicate employees automatically. Use when user says 'remove duplicates', 'clean up duplicates', or 'find duplicate employees'.
        Keeps the oldest record for each duplicate (earliest join_date).
        """
        result = await EmployeeService.delete_duplicates()
        return json.dumps(result, indent=2)
