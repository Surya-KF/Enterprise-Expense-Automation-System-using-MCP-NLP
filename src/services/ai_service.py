"""
AI Service Module
Handles AI-powered analysis using Google Gemini
"""
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import google.generativeai as genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.database.connection import get_db_connection
from src.services.department_service import DepartmentService


class AIService:
    """Service for AI-powered company analysis"""
    
    @staticmethod
    async def call_ai_api(prompt: str) -> str:
        """
        Call Google Gemini AI API with the given prompt.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            AI response text
            
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
            raise ValueError("GEMINI_API_KEY not configured in .env file")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    
    @staticmethod
    async def get_all_departments_summary() -> List[Dict[str, Any]]:
        """
        Get summary for all departments.
        
        Returns:
            List of department summaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM departments ORDER BY name")
        departments = [row["name"] for row in cursor.fetchall()]
        conn.close()
        
        summaries = []
        dept_service = DepartmentService()
        for dept_name in departments:
            summary = await dept_service.get_department_summary(dept_name)
            if summary["status"] == "success":
                summaries.append(summary)
        
        return summaries
    
    @staticmethod
    async def analyze_company(query: str) -> Dict[str, Any]:
        """
        Analyze company data using AI.
        
        Args:
            query: Natural language query about company data
            
        Returns:
            Analysis results with AI insights
        """
        try:
            # Gather comprehensive data
            summaries = await AIService.get_all_departments_summary()
            
            # Get overall company stats
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM employees")
            total_employees = cursor.fetchone()["count"]
            
            cursor.execute("SELECT SUM(salary) as total FROM employees")
            total_salary = cursor.fetchone()["total"] or 0
            
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE date >= ?", (thirty_days_ago,))
            total_expenses_30d = cursor.fetchone()["total"] or 0
            
            conn.close()
            
            # Build AI prompt
            prompt = f"""
You are an expert company analytics assistant analyzing a tech company with 4 departments: Admin, HR, Tech, and BPO.

COMPANY OVERVIEW:
- Total Employees: {total_employees}
- Total Salary Burden: ${total_salary:,.2f}
- Total Expenses (Last 30 Days): ${total_expenses_30d:,.2f}

DEPARTMENT SUMMARIES:
{json.dumps(summaries, indent=2)}

USER QUERY: "{query}"

Please provide:
1. A direct answer to the user's question
2. Key insights and patterns you observe in the data
3. Specific recommendations based on the data
4. Any concerns or red flags worth noting

Format your response as a clear, structured analysis that is both data-driven and actionable.
"""
            
            # Call AI API
            analysis = await AIService.call_ai_api(prompt)
            
            return {
                "status": "success",
                "query": query,
                "analysis": analysis,
                "data_scope": {
                    "total_employees": total_employees,
                    "departments_analyzed": len(summaries),
                    "expense_period": f"Last 30 days ({thirty_days_ago} to {datetime.now().strftime('%Y-%m-%d')})"
                },
                "ai_provider": f"GEMINI {GEMINI_MODEL.upper()}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error in AI analysis: {str(e)}"
            }
