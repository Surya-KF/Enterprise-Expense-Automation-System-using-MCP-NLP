"""
Tech Company Expense Tracker - MCP Server
Professional modular architecture with clean separation of concerns

Entry point for the FastMCP server
"""
from fastmcp import FastMCP

from src.database.schema import init_database
from src.tools import (
    register_employee_tools,
    register_department_tools,
    register_expense_tools,
    register_performance_tools,
    register_ai_tools
)
from src.config import APP_NAME, APP_VERSION


def create_mcp_server() -> FastMCP:
    """
    Create and configure the FastMCP server.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize database
    init_database()
    
    # Create MCP server
    mcp = FastMCP(APP_NAME)
    
    # Register all tool categories
    register_employee_tools(mcp)
    register_department_tools(mcp)
    register_expense_tools(mcp)
    register_performance_tools(mcp)
    register_ai_tools(mcp)
    
    return mcp


# Create server instance
mcp = create_mcp_server()


if __name__ == "__main__":
    print(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
    print("📦 Modular Architecture:")
    print("   ├── src/database/    - Database layer")
    print("   ├── src/models/      - Data models")
    print("   ├── src/services/    - Business logic")
    print("   └── src/tools/       - MCP tool wrappers")
    print("\n✅ Server ready!")
    mcp.run()
