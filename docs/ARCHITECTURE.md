# Professional Modular Architecture

## 📁 Project Structure

```
Expense Tracker/
├── main_new.py                 # Entry point (NEW modular version)
├── main.py                     # Old monolithic version (backup)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── README.md                   # Documentation
│
├── data/                       # Database files
│   ├── company.db             # SQLite database
│   └── .gitkeep
│
├── config/                     # Configuration files
│   └── departments.json       # Department definitions
│
├── src/                        # Source code (NEW)
│   ├── __init__.py
│   ├── config.py              # Centralized configuration
│   │
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py     # Database connections
│   │   ├── schema.py         # Schema initialization
│   │   └── queries.py        # Helper queries
│   │
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── employee.py       # Employee model
│   │   ├── department.py     # Department model
│   │   ├── expense.py        # Expense model
│   │   └── performance.py    # Performance model
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── employee_service.py      # Employee operations
│   │   ├── department_service.py    # Department operations
│   │   ├── expense_service.py       # Expense operations
│   │   ├── performance_service.py   # Performance operations
│   │   └── ai_service.py            # AI analysis
│   │
│   ├── tools/                 # MCP tool wrappers
│   │   ├── __init__.py
│   │   ├── employee_tools.py        # Employee MCP tools
│   │   ├── department_tools.py      # Department MCP tools
│   │   ├── expense_tools.py         # Expense MCP tools
│   │   ├── performance_tools.py     # Performance MCP tools
│   │   └── ai_tools.py              # AI MCP tools
│   │
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── validators.py     # Input validation
│       └── formatters.py     # Output formatting
│
├── scripts/                    # Utility scripts
│   ├── populate_data.py       # Database population
│   └── db_viewer.py           # Database viewer
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # This file
    ├── QUICK_REFERENCE.md
    └── GETTING_STARTED.md
```

## 🏗️ Architecture Layers

### 1. **Entry Point Layer** (`main_new.py`)
- Server initialization
- Tool registration
- Startup configuration

### 2. **Tool Layer** (`src/tools/`)
- MCP tool wrappers
- Input/output formatting
- Tool descriptions for Claude

### 3. **Service Layer** (`src/services/`)
- Business logic
- Data validation
- Transaction management
- Error handling

### 4. **Database Layer** (`src/database/`)
- Database connections
- Schema management
- Query helpers
- Data access

### 5. **Model Layer** (`src/models/`)
- Data structures
- Type definitions
- Model validation

### 6. **Utils Layer** (`src/utils/`)
- Validation functions
- Formatters
- Helper utilities

## 🔄 Request Flow

```
Claude Desktop
    ↓
MCP Tool (src/tools/)
    ↓
Service Layer (src/services/)
    ↓
Database Layer (src/database/)
    ↓
SQLite Database (data/company.db)
```

## ✨ Benefits of This Structure

### 1. **Separation of Concerns**
- Each module has a single responsibility
- Easy to locate and fix bugs
- Clear boundaries between layers

### 2. **Maintainability**
- Small, focused files (100-300 lines each)
- Easy to understand and modify
- No code duplication

### 3. **Testability**
- Each component can be tested independently
- Mock dependencies easily
- Unit test each service

### 4. **Scalability**
- Add new features without touching existing code
- Easy to add new tools or services
- Modular imports

### 5. **Debugging**
- Clear error paths
- Isolated components
- Easy to trace issues

## 📊 Module Responsibilities

| Module | Responsibility | Size |
|--------|---------------|------|
| `config.py` | Configuration management | ~40 lines |
| `database/connection.py` | DB connections | ~20 lines |
| `database/schema.py` | Schema initialization | ~80 lines |
| `database/queries.py` | Helper queries | ~60 lines |
| `services/employee_service.py` | Employee business logic | ~250 lines |
| `services/department_service.py` | Department business logic | ~200 lines |
| `services/expense_service.py` | Expense business logic | ~180 lines |
| `services/performance_service.py` | Performance business logic | ~80 lines |
| `services/ai_service.py` | AI analysis logic | ~150 lines |
| `tools/*.py` | MCP tool wrappers | ~50-100 lines each |

## 🔧 How to Extend

### Adding a New Feature

1. **Add Model** (if needed)
   ```python
   # src/models/new_feature.py
   @dataclass
   class NewFeature:
       field1: str
       field2: int
   ```

2. **Add Service**
   ```python
   # src/services/new_feature_service.py
   class NewFeatureService:
       @staticmethod
       async def create_feature(...):
           # Business logic here
   ```

3. **Add Tool Wrapper**
   ```python
   # src/tools/new_feature_tools.py
   def register_new_feature_tools(mcp):
       @mcp.tool(name="new_tool")
       async def new_tool(...):
           result = await NewFeatureService.create_feature(...)
           return json.dumps(result)
   ```

4. **Register in main_new.py**
   ```python
   from src.tools import register_new_feature_tools
   register_new_feature_tools(mcp)
   ```

## 🚀 Usage

### Running the New Modular Server

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the new modular server
python main_new.py
```

### Claude Desktop Configuration

Update `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": [
        "C:\\Users\\VH0000812\\Desktop\\Expense Tracker\\main_new.py"
      ],
      "cwd": "C:\\Users\\VH0000812\\Desktop\\Expense Tracker"
    }
  }
}
```

## 🔍 Debugging Guide

### Finding Issues

1. **Tool not working?**
   → Check `src/tools/` for tool wrapper
   → Verify registration in `main_new.py`

2. **Business logic error?**
   → Check `src/services/` for the relevant service
   → Add logging to trace the issue

3. **Database error?**
   → Check `src/database/queries.py`
   → Verify connection in `connection.py`

4. **Configuration issue?**
   → Check `src/config.py`
   → Verify `.env` file

### Adding Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In any service
logger.debug(f"Processing request: {data}")
```

## 📝 Comparison: Old vs New

| Aspect | Old (main.py) | New (Modular) |
|--------|--------------|---------------|
| **File Count** | 1 file (1088 lines) | 25+ files (~100-250 lines each) |
| **Debugging** | Scroll through 1000 lines | Jump to specific module |
| **Adding Features** | Edit monolith | Add new module |
| **Testing** | Test entire file | Test individual modules |
| **Team Work** | Merge conflicts | Parallel development |
| **Code Reuse** | Copy-paste | Import module |

## 🎯 Best Practices

1. **Keep services focused** - One service per entity type
2. **Use type hints** - Better IDE support and documentation
3. **Handle errors gracefully** - Return status dicts, don't crash
4. **Document functions** - Docstrings for all public methods
5. **Validate inputs** - Check data before database operations
6. **Log important events** - Debug issues in production

## 🔮 Future Improvements

1. **Add Logging** - Structured logging with levels
2. **Add Tests** - Unit tests for each service
3. **Add Caching** - Cache frequent queries
4. **Add Migrations** - Database schema versioning
5. **Add API Layer** - REST API alongside MCP
6. **Add Monitoring** - Performance metrics and alerts
