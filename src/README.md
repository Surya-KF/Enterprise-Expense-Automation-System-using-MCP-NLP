# src/ - Source Code

This directory contains the professional modular architecture for the Expense Tracker MCP Server.

## 📁 Directory Structure

```
src/
├── config.py              # Configuration management
├── database/              # Data access layer
├── models/                # Data models (DTOs)
├── services/              # Business logic
├── tools/                 # MCP tool wrappers
└── utils/                 # Utility functions
```

## 📦 Modules

### config.py
Centralized configuration for paths, API keys, and settings.
- Database paths
- API configuration
- Application settings

### database/
Database layer for SQLite operations.
- `connection.py` - Connection management
- `schema.py` - Schema initialization
- `queries.py` - Helper query functions

### models/
Data models representing business entities.
- `employee.py` - Employee data structure
- `department.py` - Department data structure
- `expense.py` - Expense data structure
- `performance.py` - Performance rating structure

### services/
Business logic for all operations.
- `employee_service.py` - Employee CRUD operations
- `department_service.py` - Department CRUD operations
- `expense_service.py` - Expense CRUD operations
- `performance_service.py` - Performance rating operations
- `ai_service.py` - AI-powered analysis

### tools/
MCP tool wrappers for Claude Desktop integration.
- `employee_tools.py` - Employee MCP tools
- `department_tools.py` - Department MCP tools
- `expense_tools.py` - Expense MCP tools
- `performance_tools.py` - Performance MCP tools
- `ai_tools.py` - AI analysis MCP tools

### utils/
Utility functions for validation and formatting.
- `validators.py` - Input validation functions
- `formatters.py` - Output formatting functions

## 🔄 Data Flow

```
Claude Desktop
    ↓
MCP Tool (tools/)
    ↓
Service (services/)
    ↓
Database Layer (database/)
    ↓
SQLite Database
```

## 💡 Design Principles

1. **Separation of Concerns** - Each module has one responsibility
2. **Single Responsibility** - Each function does one thing well
3. **DRY (Don't Repeat Yourself)** - Reusable components
4. **Clear Dependencies** - Explicit imports, no circular dependencies
5. **Type Hints** - Better IDE support and documentation

## 🚀 Usage

Import from the src package:

```python
from src.services import EmployeeService
from src.database import get_db_connection
from src.config import DB_PATH
```

## 📝 Adding New Features

1. Add model in `models/` if needed
2. Create service in `services/`
3. Create tool wrapper in `tools/`
4. Register tool in `main_new.py`

See `docs/ARCHITECTURE.md` for detailed guide.
