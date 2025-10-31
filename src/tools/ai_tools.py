"""
AI Analysis MCP Tools
Tool wrappers for AI-powered analysis
"""
import json
from fastmcp import FastMCP

from src.services.ai_service import AIService


def register_ai_tools(mcp: FastMCP):
    """Register AI-powered analysis tools"""
    
    @mcp.tool(name="analyze_company_with_ai")
    async def analyze_company_with_ai_tool(query: str) -> str:
        """
        Get AI-powered insights and analysis about company data. Use for complex queries like 'which department spends most', 
        'analyze trends', 'budget recommendations', 'identify issues', or any analytical question. 
        This is the MOST POWERFUL tool for natural language queries.
        
        Args:
            query: Natural language question or analysis request about the company
        """
        result = await AIService.analyze_company(query)
        return json.dumps(result, indent=2)
