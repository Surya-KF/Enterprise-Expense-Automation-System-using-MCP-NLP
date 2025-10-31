"""
Performance MCP Tools
Tool wrappers for performance rating operations
"""
import json
from fastmcp import FastMCP

from src.services.performance_service import PerformanceService


def register_performance_tools(mcp: FastMCP):
    """Register performance-related MCP tools"""
    
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
        result = await PerformanceService.add_performance(employee_name, rating, month, comments)
        return json.dumps(result, indent=2)
