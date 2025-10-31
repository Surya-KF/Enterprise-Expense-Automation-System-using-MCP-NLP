# Changelog

All notable changes to the Company Expense Tracker MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-15

### Changed
- 🚀 **Updated AI Model**: Upgraded from `gemini-pro` to `gemini-2.0-flash-exp`
  - Using the latest Gemini 2.0 Flash experimental model (2025)
  - Improved AI analysis performance and accuracy
  - Better natural language understanding

### Technical Details
- Model change: `genai.GenerativeModel('gemini-2.0-flash-exp')`
- Updated documentation to reflect latest AI capabilities
- Maintained backward compatibility with existing API key configuration

## [1.0.0] - 2025-10-15

### Added
- 🎉 Initial production release
- 12 MCP tools for complete CRUD operations
- Employee number system (EMP0001, EMP0002, etc.)
- 4 delete operations with cascade support
- Duplicate employee detection and cleanup
- AI-powered analysis with Google Gemini Pro
- Professional project structure with organized directories
- Comprehensive documentation suite
- Interactive database viewer (`scripts/db_viewer.py`)
- Migration scripts for database updates
- Complete test suite

### Features
#### Create Operations (4 tools)
- `add_department` - Create new departments
- `add_employee` - Add employees with auto-generated employee numbers
- `add_expense` - Track expenses by department and category
- `add_performance` - Add employee performance ratings

#### Delete Operations (4 tools)
- `delete_employee` - Remove employees by employee_number or name
- `delete_expense` - Delete expense records by ID
- `delete_department` - Remove departments (with safe/force modes)
- `delete_duplicate_employees` - Auto-detect and remove duplicate employees

#### Query Operations (3 tools)
- `list_employees` - List all employees or filter by department
- `list_expenses` - List expenses with optional filters
- `get_department_summary` - Comprehensive department statistics

#### AI Analysis (1 tool)
- `analyze_company_with_ai` - AI-powered company insights using Gemini Pro

### Database Schema
- 4 tables: departments, employees, expenses, performance
- Foreign key relationships and cascade deletes
- Indexed columns for performance
- Employee number uniqueness constraint

### Project Structure
```
├── src/              # Source code modules
├── tests/            # Test files
├── scripts/          # Utility scripts
├── docs/             # Documentation
├── config/           # Configuration files
├── data/             # Database files
```

### Documentation
- README.md - Main documentation
- QUICK_REFERENCE.md - Quick reference card for all tools
- COMPLETE_SUMMARY.md - Comprehensive system overview
- DELETE_TOOLS.md - Delete operations guide
- GETTING_STARTED.md - Setup guide

### Security
- API keys in environment variables
- Input validation on all operations
- Safe delete mode (prevents accidental data loss)
- Foreign key constraints enforced

### Testing
- test_tools.py - MCP tools verification
- test_delete_functions.py - Delete operations testing
- test_employee_numbers.py - Employee number system validation

### Bug Fixes
- Fixed absolute path resolution for database (was using relative paths)
- Fixed tool naming issues (FastMCP name parameter)
- Fixed JSON communication errors (removed stdout pollution)
- Fixed Gemini model version (gemini-1.5-pro → gemini-pro)
- Fixed duplicate employee data in database

### Performance
- Added database indexes on frequently queried columns
- Optimized queries for department summaries
- Efficient cascade delete operations

## [0.9.0] - 2025-10-14

### Added
- Initial MCP server implementation
- Basic CRUD operations
- SQLite database setup
- FastMCP integration

### Known Issues
- Relative paths causing issues in Claude Desktop
- Duplicate employees in database
- Tool naming mismatches

## [0.8.0] - 2025-10-13

### Added
- Project initialization
- Basic database schema
- Initial tool definitions

---

## Future Releases

### [1.1.0] - Planned
- Update/edit operations for employees and expenses
- Bulk import/export functionality
- Enhanced error messages
- Performance optimizations

### [1.2.0] - Planned
- Monthly and yearly report generation
- Budget tracking with alerts
- Email notifications for important events
- Advanced analytics dashboard

### [2.0.0] - Planned
- REST API endpoints
- Web-based dashboard
- Multi-tenant support
- Role-based access control
- Audit logging

---

## Version History

- **1.0.0** (2025-10-15) - Production release with 12 tools ✅
- **0.9.0** (2025-10-14) - Beta release with basic functionality
- **0.8.0** (2025-10-13) - Alpha release with initial setup

[1.0.0]: https://github.com/company/expense-tracker/releases/tag/v1.0.0
[0.9.0]: https://github.com/company/expense-tracker/releases/tag/v0.9.0
[0.8.0]: https://github.com/company/expense-tracker/releases/tag/v0.8.0
