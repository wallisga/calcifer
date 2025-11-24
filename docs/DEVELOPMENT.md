# Development Setup

Guide for setting up Calcifer for local development.

## Prerequisites

See [PREREQUISITES.md](PREREQUISITES.md) for system requirements.

**Quick checklist:**
- Python 3.11+
- Git
- VS Code (recommended)

## Setup from Git Clone

### 1. Clone Repository
```bash
git clone git@github.com:yourusername/calcifer.git
cd calcifer
```

### 2. Set Up Python Environment
```bash
cd calcifer-app
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Initialize Local Documentation

The repo includes template documentation, but local changes are git-ignored:
```bash
cd ..
# docs/CHANGES.md will be created automatically by Calcifer
# You can also create it manually:
cat > docs/CHANGES.md << 'EOF'
# Change Log

## $(date +%Y-%m-%d) - $(git config user.name)
- Initial local setup
EOF
```

### 4. Run Calcifer
```bash
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000

### 5. Make Initial Commit (If Needed)

If this is a fresh repo without commits:
```bash
cd ~/calcifer
git add .
git commit -m "Initial setup"
```

---

## Development Workflow

### Using VS Code

Open the repository in VS Code:
```bash
code ~/calcifer
```

**Recommended Extensions:**
- Python (ms-python.python)
- Pylance (for Python intellisense)
- GitLens (for Git integration)

**VS Code Tasks:**

Press `Ctrl+Shift+P` → "Run Task":
- "Run Calcifer (Development)" - Starts the server
- "Open Calcifer Dashboard" - Opens browser

---

## File Structure (Post Phase 2 Refactoring)

```
calcifer/
├── calcifer-app/           # Application code
│   ├── src/               # Python source
│   │   ├── main.py       # FastAPI routes (thin layer, <20 lines each)
│   │   │
│   │   ├── core/         # Core modules (REQUIRED)
│   │   │   ├── __init__.py
│   │   │   ├── work_module.py              # Work item management
│   │   │   ├── service_catalog_module.py   # Service catalog
│   │   │   ├── documentation_module.py     # Documentation management
│   │   │   ├── git_module.py               # Local Git operations
│   │   │   └── settings_module.py          # Configuration
│   │   │
│   │   ├── integrations/  # Optional integrations
│   │   │   ├── __init__.py
│   │   │   └── monitoring/
│   │   │       ├── integration.py          # Low-level health checks
│   │   │       └── endpoint_module.py      # Business logic
│   │   │
│   │   ├── models.py     # Database models (SQLAlchemy)
│   │   ├── schemas.py    # API schemas (Pydantic)
│   │   └── database.py   # DB configuration
│   │
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # CSS/JS (currently minimal)
│   ├── data/             # SQLite database (git-ignored)
│   └── requirements.txt  # Python dependencies
│
├── docs/                 # Documentation
│   ├── ROADMAP.md
│   ├── SETUP_GUIDE.md
│   ├── PREREQUISITES.md
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_PATTERNS_GUIDE.md  # ← Key reference!
│   ├── DEVELOPER_QUICK_REFERENCE.md    # ← Keep this handy!
│   ├── CHANGES.md        # Tracked change log
│   └── endpoint-*.md     # Generated endpoint docs
│
├── infrastructure/       # Deployment configs (future)
└── README.md
```

---

## Architecture Overview (Phase 2)

Calcifer uses a **clean three-layer architecture**:

### Layer 1: HTTP/UI (main.py)
- **Purpose:** Routing only
- **Rules:** 
  - ✅ Parse requests
  - ✅ Call module methods
  - ✅ Return responses
  - ❌ No business logic
  - ❌ No database queries (except simple display)

### Layer 2: Modules (core/* and integrations/*)
- **Purpose:** All business logic
- **Rules:**
  - ✅ Validation
  - ✅ Database operations
  - ✅ Orchestration
  - ❌ No HTTP concerns
  - ❌ No template rendering

### Layer 3: Data (models.py, database.py)
- **Purpose:** Database schema
- **Rules:**
  - ✅ ORM models
  - ✅ Basic queries
  - ❌ No business logic

---

## Making Changes

### Step 1: Create Work Item
Use Calcifer UI to create a work item → auto-creates Git branch

### Step 2: Decide Where Code Goes

**Is it required for Calcifer to work?**
- YES → `src/core/` (core module)
- NO → `src/integrations/` (integration module)

**Is it HTTP routing?**
- YES → `src/main.py` (keep it thin!)
- NO → Add to appropriate module

**Is it a database model?**
- YES → `src/models.py`
- NO → Somewhere else

### Step 3: Write Code

**For routes (main.py):**
```python
@app.post("/resource/action")
async def perform_action(
    param: str = Form(...),
    db: Session = Depends(get_db)
):
    """Short docstring."""
    # Call module - it does everything
    success, message = module.perform_action(db, param)
    
    # Redirect based on result
    if success:
        return RedirectResponse(url=f"/success?message={message}", status_code=303)
    else:
        return RedirectResponse(url=f"/error?message={message}", status_code=303)
```

**For modules:**
```python
# In src/core/your_module.py

@staticmethod
def perform_action(db: Session, param: str) -> Tuple[bool, str]:
    """
    Brief description.
    
    Args:
        db: Database session
        param: Description
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validation
    if not param:
        return False, "Param required"
    
    # Business logic
    processed = param.lower().strip()
    
    # Database operations
    obj = models.YourModel(value=processed)
    db.add(obj)
    db.commit()
    
    return True, "Success!"
```

### Step 4: Test Locally
```bash
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload
```

### Step 5: Update Documentation
- Add notes in the work item
- Calcifer will prompt for CHANGES.md entry when committing

### Step 6: Commit
Use Calcifer's "Commit Changes" button to commit with CHANGES.md update

---

## Key Development References

### Must-Read Before Coding
1. **[ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md)** - Detailed patterns
2. **[DEVELOPER_QUICK_REFERENCE.md](../docs/DEVELOPER_QUICK_REFERENCE.md)** - Daily cheat sheet

### Golden Rules
1. **Routes are thin** - 5-15 lines, no business logic
2. **Modules are thick** - ALL business logic here
3. **Core can't use integrations** - Must work standalone
4. **Return `Tuple[bool, str]`** - For operations that can fail

---

## Database

Calcifer uses SQLite stored in `calcifer-app/data/calcifer.db`.

### Inspect Database
```bash
cd calcifer-app
sqlite3 data/calcifer.db

.tables
SELECT * FROM work_items;
.quit
```

### Reset Database (Fresh Start)
```bash
rm -f calcifer-app/data/calcifer.db
# Restart Calcifer - database will be recreated
```

### Database Migrations (Future)
Currently, schema changes require manual migration or DB reset.  
**Planned:** Alembic migrations in Phase 3

---

## Common Issues

### Port 8000 in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Import errors
```bash
cd calcifer-app
source venv/bin/activate
pip install -r requirements.txt
```

### Module not found
```bash
# Check your imports
# Core modules: from .core import module_name
# Integrations: from .integrations import module_name

# Verify __init__.py exists
ls src/core/__init__.py
ls src/integrations/__init__.py
```

### Database errors
```bash
rm -f calcifer-app/data/calcifer.db
# Restart - fresh database
```

### Git branch issues
```bash
# Check current branch
git branch

# Switch back to main
git checkout main

# See all branches
git branch -a
```

---

## Testing (Future - Phase 3)

Testing infrastructure is planned for Phase 3.

**Planned approach:**
```python
# Unit test example (future)
def test_create_work_item():
    # Arrange
    db = mock_db()
    
    # Act
    result = work_module.create_work_item(db, "Test", "service", "new")
    
    # Assert
    assert result.title == "Test"
    assert result.git_branch is not None
```

**See ROADMAP.md for testing priorities**

---

## Code Quality Checklist

Before committing, verify:

- [ ] Routes under 20 lines?
- [ ] No business logic in routes?
- [ ] Module methods have docstrings?
- [ ] Proper return types (Tuple[bool, str] for actions)?
- [ ] Core modules don't import integrations?
- [ ] Using singleton instances (e.g., `work_module` not `WorkModule`)?
- [ ] Error messages user-friendly?
- [ ] CHANGES.md updated?
- [ ] Tested manually?

---

## Development Workflow Summary

```
1. Create work item in UI
   ↓
2. Branch created automatically
   ↓
3. Write code in appropriate module
   ↓
4. Test locally (uvicorn --reload)
   ↓
5. Add notes to work item
   ↓
6. Use "Commit Changes" button
   ↓
7. Complete checklist
   ↓
8. "Merge & Complete" when done
```

---

## Module Development Patterns

### Adding a New Core Module

1. Create file in `src/core/`
2. Define class with @staticmethod methods
3. Create singleton instance at bottom
4. Export in `src/core/__init__.py`
5. Use in routes

**Example:**
```python
# src/core/new_module.py

class NewModule:
    """Module description."""
    
    @staticmethod
    def do_something(db: Session, param: str) -> Tuple[bool, str]:
        """Method description."""
        # Implementation
        return True, "Success"

# Singleton
new_module = NewModule()
```

```python
# src/core/__init__.py
from .new_module import new_module

__all__ = [..., 'new_module']
```

### Adding a New Integration

1. Create directory in `src/integrations/`
2. Create `integration.py` (low-level operations)
3. Create `module_name.py` (business logic)
4. Create `__init__.py` (exports)
5. Use in routes

**See [ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md) Section: "Pattern 3: Integration Modules"**

---

## Performance Tips

### Development Mode
```bash
# Enable auto-reload (default in command above)
uvicorn src.main:app --reload

# Use different port if needed
uvicorn src.main:app --reload --port 8001
```

### Database Performance
- SQLite is fast for < 100k records
- Add indexes for frequently queried fields (future)
- Consider PostgreSQL for production (future)

### Git Performance
- Keep repo size reasonable (< 1GB)
- Don't commit large files
- Use `.gitignore` properly

---

## Debugging

### Enable Debug Logging
```python
# In src/main.py (temporarily)
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Route Registration
```bash
# Start server and check this URL
curl http://localhost:8000/docs
# Shows all registered routes
```

### Inspect Module State
```python
# In a route (temporarily)
print(f"Module state: {module.get_all_data()}")
```

---

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Check [ROADMAP.md](ROADMAP.md) for planned features
- Review [ARCHITECTURE_PATTERNS_GUIDE.md](../docs/ARCHITECTURE_PATTERNS_GUIDE.md) for detailed patterns
- Keep [DEVELOPER_QUICK_REFERENCE.md](../docs/DEVELOPER_QUICK_REFERENCE.md) handy while coding
- Start building! 🔥

---

**Remember:** If your route is more than 20 lines or has business logic, something is wrong! Move that logic to a module. 😄