# Calcifer Developer Quick Reference

**Keep this handy when adding features or fixing bugs!**

---

## 🎯 The Golden Rules

1. **Routes are thin** - 5-15 lines, no business logic
2. **Modules are thick** - ALL business logic lives here
3. **Core can't use integrations** - Must work standalone
4. **Integrations can use core** - Composition is good
5. **Return `Tuple[bool, str]`** - For operations that can fail

---

## 📁 Where Does Code Go?

```
Is it required for Calcifer?
    ├─ YES → src/core/
    └─ NO  → src/integrations/

Is it HTTP routing?
    ├─ YES → src/main.py (keep it thin!)
    └─ NO  → In a module

Is it a database model?
    ├─ YES → src/models.py
    └─ NO  → Not here

Is it validation?
    ├─ YES → In the module method
    └─ NO  → Maybe it's transformation?
```

---

## ✅ Perfect Route Example

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

**That's it! 9 lines. Perfect.** ✨

---

## ❌ Anti-Pattern Alert

**DON'T do this in routes:**

```python
@app.post("/bad-example")
async def bad_route(title: str = Form(...), db: Session = Depends(get_db)):
    # ❌ Validation
    if len(title) < 3:
        return RedirectResponse(url="/?error=Too short")
    
    # ❌ Business logic
    slug = title.lower().replace(" ", "-")
    
    # ❌ Database operations
    item = models.Item(title=title, slug=slug)
    db.add(item)
    db.commit()
    
    return RedirectResponse(...)
```

**Instead, do this:**

```python
@app.post("/good-example")
async def good_route(title: str = Form(...), db: Session = Depends(get_db)):
    # ✅ Just call the module
    item = item_module.create_item(db, title)
    return RedirectResponse(url=f"/items/{item.id}", status_code=303)
```

---

## 🔧 Module Method Template

```python
# In src/core/your_module.py

@staticmethod
def do_something(db: Session, param: str) -> Tuple[bool, str]:
    """
    Brief description.
    
    Args:
        db: Database session
        param: Description
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Step 1: Validate
    if not param or len(param) < 3:
        return False, "Param too short"
    
    # Step 2: Business logic
    processed = param.lower().strip()
    
    # Step 3: Database operations
    obj = models.YourModel(value=processed)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    # Step 4: Return result
    return True, "Created successfully"
```

---

## 🏗️ Adding a New Feature Checklist

- [ ] **Decide:** Core or Integration?
  - Required? → Core (`src/core/`)
  - Optional? → Integration (`src/integrations/`)

- [ ] **Create/Update Module:**
  - Add method with business logic
  - Add validation
  - Add docstring (Args, Returns)
  - Return appropriate type

- [ ] **Create Route:**
  - GET: Fetch data, render template
  - POST: Parse form, call module, redirect
  - Keep under 15 lines
  - No business logic!

- [ ] **Create/Update Template:**
  - Receives data from route
  - Shows success/error messages
  - Forms POST to routes

- [ ] **Test:**
  - Happy path works
  - Error cases work
  - Route is thin
  - Module has logic

---

## 📚 Common Imports

```python
# In main.py
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .core import (
    work_module,
    service_catalog_module,
    documentation_module,
    git_module,
    settings_module
)
from .integrations import monitoring, endpoint_module

# In modules
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from datetime import datetime
from .. import models
from .git_module import git_module  # Core can use other core
```

---

## 🎨 Return Type Guide

| Operation | Return Type | Example |
|-----------|-------------|---------|
| Create | `Model` | `return work_item` |
| Get | `Optional[Model]` | `return work_item or None` |
| List | `List[Model]` | `return [item1, item2]` |
| Action | `Tuple[bool, str]` | `return True, "Success!"` |
| Complex | `dict` | `return {"item": ..., "meta": ...}` |

---

## 🚦 Module Method Patterns

### Pattern 1: Create Something
```python
@staticmethod
def create_thing(db: Session, name: str) -> models.Thing:
    thing = models.Thing(name=name)
    db.add(thing)
    db.commit()
    db.refresh(thing)
    return thing
```

### Pattern 2: Action with Validation
```python
@staticmethod
def do_thing(db: Session, id: int) -> Tuple[bool, str]:
    thing = db.query(models.Thing).filter(...).first()
    if not thing:
        return False, "Not found"
    
    if thing.status != "ready":
        return False, "Not ready yet"
    
    thing.status = "done"
    db.commit()
    return True, "Action completed!"
```

### Pattern 3: Get with Relations
```python
@staticmethod
def get_thing_detail(db: Session, id: int) -> Optional[dict]:
    thing = db.query(models.Thing).filter(...).first()
    if not thing:
        return None
    
    related = db.query(models.Related).filter(...).all()
    
    return {
        "thing": thing,
        "related": related,
        "meta": some_calculation()
    }
```

---

## 🔍 Quick Debugging

**Route too long?**
→ Move logic to module

**Module doing HTTP stuff?**
→ Move to route, module should return data

**Core module importing integration?**
→ Wrong! Reverse the dependency

**Direct DB query in route?**
→ Move to module (unless simple display)

**Business logic in route?**
→ Move to module

---

## 📖 Documentation Standards

### Docstring Template
```python
def method_name(param1: Type, param2: Type) -> ReturnType:
    """
    Brief one-line description.
    
    Longer description if needed. Explain what this does,
    not how it does it (code shows that).
    
    Args:
        param1: What is this parameter
        param2: What is this parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something specific goes wrong (optional)
    """
```

### Module Header Template
```python
"""
Module Name Module

Handles [domain] functionality.
[Required/Optional] for Calcifer - [explain why].
"""
```

---

## 🧪 Testing Checklist (Future)

```python
# Unit test template (when we add pytest)
def test_create_thing():
    # Arrange
    db = mock_db()
    
    # Act
    result = module.create_thing(db, "test")
    
    # Assert
    assert result.name == "test"
    assert result.id is not None
```

---

## 🎯 Code Review Checklist

Before committing:

- [ ] Routes under 20 lines?
- [ ] No business logic in routes?
- [ ] Module methods have docstrings?
- [ ] Proper return types?
- [ ] Core modules don't import integrations?
- [ ] Using singleton instances (not classes)?
- [ ] Proper error messages for users?
- [ ] CHANGES.md updated?
- [ ] Tested manually?

---

## 🚀 Quick Commands

```bash
# Start development
cd calcifer-app
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Check if modules are importable
python -c "from src.core import work_module; print('✅ OK')"

# Reset database (careful!)
rm -f data/calcifer.db
# Restart app - will recreate

# View logs
# In terminal where uvicorn is running
```

---

## 📊 Current Metrics

**Target Route Length:** ≤15 lines  
**Current Average:** ~20 lines  
**Progress:** 68% of routes are excellent  

**Goal:** 100% routes under 20 lines

---

## 🔗 Related Documentation

- `ARCHITECTURE_PATTERNS_GUIDE.md` - Detailed patterns
- `ARCHITECTURE.md` - High-level overview
- `REFACTORING_ACTION_PLAN.md` - Current tasks
- `DOCUMENTATION_AUDIT_REPORT.md` - Status check

---

## 💡 Remember

> "A route should be so simple that it's boring to read.  
> All the interesting stuff happens in the modules."

**If your route is interesting, something is wrong!** 😄

---

**Last Updated:** November 23, 2025  
**Keep this file updated as patterns evolve!**