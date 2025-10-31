# Migration Guide: Monolithic → Modular

## 🎯 Quick Start

### Step 1: Backup Old Version
The old `main.py` has been kept as backup. The new version is `main_new.py`.

### Step 2: Update Claude Desktop Config

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

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

### Step 3: Test the New Server

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Test the new modular server
python main_new.py
```

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop to load the new server.

## 📊 What Changed?

| Old Structure | New Structure |
|--------------|---------------|
| Single `main.py` (1088 lines) | 25+ modular files |
| All code in one file | Organized by responsibility |
| Hard to debug | Easy to locate issues |
| Hard to extend | Add new modules easily |

## 🔧 Key Benefits

### 1. **Easy Debugging**
**Before:**
```
Error in main.py line 847
(Need to scroll through 1088 lines)
```

**After:**
```
Error in src/services/employee_service.py line 45
(Jump directly to the 250-line employee service file)
```

### 2. **Easy to Extend**
**Before:** Edit the 1088-line monolith

**After:** Add a new file:
```
src/services/new_feature_service.py  (new file)
src/tools/new_feature_tools.py       (new file)
```

### 3. **Better Organization**
```
src/
├── database/    ← All database code
├── services/    ← All business logic  
├── tools/       ← All MCP tools
└── models/      ← All data models
```

## 📁 File Mapping

| Old Location (main.py) | New Location |
|------------------------|--------------|
| Lines 1-30 (imports) | `src/config.py` |
| Lines 31-105 (DB init) | `src/database/schema.py` |
| Lines 106-135 (helpers) | `src/database/queries.py` |
| Lines 136-171 (AI) | `src/services/ai_service.py` |
| Lines 172-346 (Employee CRUD) | `src/services/employee_service.py` |
| Lines 347-450 (Department CRUD) | `src/services/department_service.py` |
| Lines 451-550 (Expense CRUD) | `src/services/expense_service.py` |
| Lines 551-620 (Performance) | `src/services/performance_service.py` |
| Lines 870-1088 (MCP tools) | `src/tools/*.py` |

## 🧪 Testing

```powershell
# Test imports
python -c "from src.services import EmployeeService; print('✅ Services import OK')"

# Test database
python -c "from src.database import init_database; init_database(); print('✅ Database OK')"

# Test configuration
python -c "from src.config import DB_PATH; print(f'✅ Config OK: {DB_PATH}')"
```

## ⚠️ Troubleshooting

### Import Errors?
```powershell
# Make sure you're in the project root
cd "C:\Users\VH0000812\Desktop\Expense Tracker"

# Python needs to find the src package
python main_new.py
```

### Claude Desktop Not Working?
1. Check config path: `%APPDATA%\Claude\claude_desktop_config.json`
2. Verify `main_new.py` path is correct
3. Restart Claude Desktop completely

### Database Issues?
The database file (`data/company.db`) is shared between old and new versions. No migration needed!

## 🎉 Success Checklist

- [ ] New structure created in `src/` folder
- [ ] `main_new.py` created
- [ ] Claude Desktop config updated
- [ ] Server starts without errors
- [ ] All 12 tools work in Claude Desktop
- [ ] Documentation read (`docs/ARCHITECTURE.md`)

## 🔄 Rollback Plan

If something goes wrong, you can always go back:

```json
{
  "mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": [
        "C:\\Users\\VH0000812\\Desktop\\Expense Tracker\\main.py"
      ]
    }
  }
}
```

The old `main.py` is still there and fully functional!

## 📚 Next Steps

1. Read `docs/ARCHITECTURE.md` for full architecture details
2. Explore the `src/` folder structure
3. Try adding a new feature (see ARCHITECTURE.md)
4. Consider adding tests (create `tests/` directory)

## 🤝 Contributing

Now that the code is modular:
- Each team member can work on different services
- Less merge conflicts
- Easier code reviews
- Better version control

---

**Remember:** Both versions work! The new modular structure is for better maintainability and debugging.
