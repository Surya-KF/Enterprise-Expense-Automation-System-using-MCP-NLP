"""
Department MCP Tools
Tool wrappers for department operations
"""
import json
from fastmcp import FastMCP

from src.services.department_service import DepartmentService


def register_department_tools(mcp: FastMCP):
    """Register department-related MCP tools"""
    
    @mcp.tool(name="add_department")
    async def add_department_tool(name: str, description: str = "") -> str:
        """
        Create a new department in the company. Use when user says 'add department', 'create new department', or 'new team'.
        
        Args:
            name: Department name (must be unique)
            description: Department description
        """
        result = await DepartmentService.add_department(name, description)
        return json.dumps(result, indent=2)
    
    @mcp.tool(name="get_department_summary")
    async def get_department_summary_tool(department_name: str) -> str:
        """
        Get comprehensive analytics and insights for a department including employees, expenses, and performance. 
        Use when user asks 'how is Tech doing', 'department overview', 'show me HR stats', or 'department report'.
        
        Args:
            department_name: Department name (Admin, HR, Tech, or BPO)
        """
        result = await DepartmentService.get_department_summary(department_name)
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
        result = await DepartmentService.delete_department(department_name, force)
        return json.dumps(result, indent=2)
