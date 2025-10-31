"""
Configuration Module
Centralized configuration for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"

# Database configuration
DB_PATH = DATA_DIR / "company.db"
DEPARTMENTS_JSON = CONFIG_DIR / "departments.json"

# API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Application settings
APP_NAME = "company-expense-tracker"
APP_VERSION = "1.1.0"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)
