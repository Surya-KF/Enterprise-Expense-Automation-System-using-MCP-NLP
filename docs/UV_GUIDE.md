# UV Package Manager - Quick Reference

## 🎯 What is UV?

UV is a fast Python package manager that replaces pip, venv, and requirements.txt with a modern, Rust-powered solution.

## 📦 Project Setup (DONE ✅)

Your project now has:
- ✅ `pyproject.toml` - Project configuration and dependencies
- ✅ `uv.lock` - Locked versions of all 121 dependencies
- ✅ `.venv/` - Virtual environment synced with locked versions

## 🚀 Common UV Commands

### Managing Dependencies

```powershell
# Sync dependencies (install/update based on uv.lock)
uv sync

# Add a new dependency
uv add <package-name>
# Example: uv add requests

# Add a dev dependency
uv add --dev pytest

# Remove a dependency
uv remove <package-name>

# Update lock file after manual pyproject.toml changes
uv lock

# Update all dependencies to latest compatible versions
uv lock --upgrade
```

### Running Commands

```powershell
# Run Python script with UV
uv run python main_new.py

# Run any command in the virtual environment
uv run <command>

# Example: Run tests
uv run pytest

# Example: Format code
uv run black src/
```

### Virtual Environment

```powershell
# Create virtual environment (done automatically with uv sync)
uv venv

# Activate virtual environment manually
.\.venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Development Tools

```powershell
# Install dev dependencies
uv sync --extra dev

# Run specific tools
uv run black src/          # Format code
uv run isort src/          # Sort imports
uv run flake8 src/         # Lint code
uv run mypy src/           # Type checking
uv run pytest tests/       # Run tests
```

## 📋 Your Project Dependencies

### Production Dependencies
- `fastmcp>=0.2.0` - MCP server framework
- `google-generativeai>=0.3.0` - Gemini AI
- `python-dotenv>=1.0.0` - Environment variables
- `streamlit>=1.31.0` - Web dashboard
- `pandas>=2.0.0` - Data analysis
- `plotly>=5.18.0` - Visualizations

### Dev Dependencies (Optional)
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `black>=23.0.0` - Code formatter
- `isort>=5.12.0` - Import sorter
- `flake8>=6.0.0` - Linter
- `mypy>=1.0.0` - Type checker

## 🔧 Useful Workflows

### Starting Fresh
```powershell
# Clone project and setup
git clone <repo>
cd expense-tracker
uv sync
```

### Adding a New Feature
```powershell
# Need a new library?
uv add new-package-name

# This automatically:
# 1. Adds to pyproject.toml
# 2. Updates uv.lock
# 3. Installs the package
```

### Before Committing Code
```powershell
# Format and check code
uv run black src/
uv run isort src/
uv run flake8 src/
uv run mypy src/

# Run tests
uv run pytest
```

### Updating Dependencies
```powershell
# Update all to latest compatible versions
uv lock --upgrade
uv sync

# Update specific package
uv add package-name@latest
```

## 🎨 Code Quality Tools (Pre-configured)

### Black (Code Formatter)
```powershell
uv run black src/
# Automatically formats to consistent style
```

### Isort (Import Sorter)
```powershell
uv run isort src/
# Sorts imports alphabetically and by type
```

### Flake8 (Linter)
```powershell
uv run flake8 src/
# Checks for code quality issues
```

### Mypy (Type Checker)
```powershell
uv run mypy src/
# Validates type hints
```

## 📊 Comparison: UV vs Traditional

| Task | Traditional | UV |
|------|-------------|-----|
| Create venv | `python -m venv .venv` | `uv venv` |
| Install deps | `pip install -r requirements.txt` | `uv sync` |
| Add package | `pip install X && pip freeze` | `uv add X` |
| Lock versions | Manual requirements.txt | Automatic uv.lock |
| Speed | Slow | 10-100x faster |

## 🎯 Best Practices

1. **Always commit uv.lock** - Ensures reproducible builds
2. **Use `uv sync`** - Not `pip install`
3. **Add dependencies with UV** - Don't edit pyproject.toml manually
4. **Keep dev deps separate** - Use `--dev` flag
5. **Update regularly** - `uv lock --upgrade` monthly

## 🐛 Troubleshooting

### Dependencies out of sync?
```powershell
uv sync --reinstall
```

### Lock file conflicts?
```powershell
uv lock --upgrade
```

### Wrong Python version?
```powershell
uv venv --python 3.11
uv sync
```

### Clean start?
```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

## 📚 Resources

- UV Docs: https://docs.astral.sh/uv/
- GitHub: https://github.com/astral-sh/uv
- Migration Guide: https://docs.astral.sh/uv/guides/migration/

## 🎉 Benefits You Get

✅ **10-100x faster** than pip
✅ **Reproducible builds** with uv.lock
✅ **No dependency hell** - exact versions locked
✅ **Simple commands** - less typing
✅ **Better caching** - shared across projects
✅ **Modern tooling** - Rust-powered speed

---

**Quick Start:**
```powershell
uv sync                    # Install dependencies
uv run python main_new.py  # Run your server
```
