# Calcifer Testing Guide

Comprehensive guide to testing patterns, practices, and infrastructure for Calcifer.

## 📊 Current Test Coverage

**As of Phase 3 (November 2025):**

| Metric | Value |
|--------|-------|
| **Total Tests** | 49 |
| **Unit Tests** | 40 |
| **Integration Tests** | 9 |
| **Overall Coverage** | 72.63% |
| **Execution Time** | 0.93 seconds |

**Module Coverage:**
- `work_module.py`: 88% ✅
- `service_catalog_module.py`: 100% ✅
- `git_module.py`: 61.74% ⚠️
- `documentation_module.py`: 52.50% ⚠️
- `settings_module.py`: 63.41% ⚠️
- `logging_module.py`: 38.10% ⚠️

---

## 🎯 Testing Philosophy

### What We Test

✅ **Business Logic** - Core functionality that affects users  
✅ **Data Transformations** - Functions that process/modify data  
✅ **Integration Points** - How modules work together  
✅ **Edge Cases** - Boundary conditions and error scenarios  
✅ **User Workflows** - End-to-end critical paths  

### What We Don't Test

❌ **Simple Getters/Setters** - No business logic  
❌ **Logging Statements** - Low value, hard to test  
❌ **Third-party Libraries** - Already tested  
❌ **Obvious Code** - `return x` doesn't need a test  
❌ **UI Rendering** - FastAPI templates (manual QA)  

### Coverage Goals

| Coverage | Target | Status |
|----------|--------|--------|
| **Core Modules** | 70%+ | ✅ 72.63% |
| **Business Logic** | 80%+ | ✅ 88% (work_module) |
| **Critical Paths** | 95%+ | ✅ (integration tests) |
| **Overall** | 70%+ | ✅ 72.63% |

**Philosophy:** Quality over quantity. 72% with good tests > 95% with bad tests.

---

## 🏗️ Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Fast, isolated tests
│   ├── test_work_module.py           # 17 tests
│   └── test_service_catalog_module.py # 23 tests
└── integration/             # Slower, real dependencies
    └── test_work_flows.py            # 9 tests
```

### Unit Tests
- **Fast** (< 0.1s per test)
- **Isolated** (mocked dependencies)
- **Focused** (one function/method)
- **No side effects** (no Git, no filesystem)

### Integration Tests
- **Slower** (1-5s per test)
- **Real dependencies** (actual Git repos, filesystem)
- **End-to-end** (full workflows)
- **Validates integration** (modules work together)

---

## 🧪 Running Tests

### Basic Commands

```bash
# All tests
pytest tests/ -v

# Only unit tests (fast)
pytest tests/unit/ -v

# Only integration tests
pytest tests/integration/ -v

# With coverage report
pytest tests/ -v --cov=src/core --cov-report=term-missing

# Stop on first failure
pytest tests/ -v -x

# Run specific test file
pytest tests/unit/test_work_module.py -v

# Run specific test
pytest tests/unit/test_work_module.py::TestWorkModule::test_create_work_item -v
```

### Advanced Commands

```bash
# Only fast tests (skip @pytest.mark.slow)
pytest tests/ -v -m "not slow"

# Verbose output with full tracebacks
pytest tests/ -vv --tb=long

# Show local variables on failure
pytest tests/ -vv --showlocals

# Generate HTML coverage report
pytest tests/ --cov=src/core --cov-report=html
# Open: htmlcov/index.html

# Parallel execution (if you add pytest-xdist)
pytest tests/ -v -n auto
```

### Configuration

See `pytest.ini` in `calcifer-app/`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, real dependencies)
    slow: Slow tests (skip with -m "not slow")
addopts = 
    -v
    --strict-markers
    --cov=src/core
    --cov-report=term-missing
```

---

## 🔧 Writing Unit Tests

### Pattern: Test a Module Method

```python
# tests/unit/test_my_module.py

import pytest
from src.core import my_module
from src import models


class TestMyModule:
    """Unit tests for MyModule."""
    
    @pytest.mark.unit
    def test_create_something(self, db_session):
        """Test creating something."""
        # Arrange
        name = "Test Item"
        
        # Act
        result = my_module.create_something(db_session, name)
        
        # Assert
        assert result.name == name
        assert result.id is not None
    
    @pytest.mark.unit
    def test_validate_input(self, db_session):
        """Test input validation."""
        # Act
        success, message = my_module.do_something(db_session, "")
        
        # Assert
        assert success is False
        assert "required" in message.lower()
```

### Key Fixtures

**`db_session`** - In-memory SQLite database
```python
def test_with_database(db_session):
    # db_session is a clean database session
    # Automatically rolled back after test
    work = models.WorkItem(title="Test")
    db_session.add(work)
    db_session.commit()
    
    assert work.id is not None
```

**Mocking Dependencies:**
```python
@pytest.mark.unit
def test_with_mocked_git(db_session, mocker):
    """Test with mocked Git operations."""
    # Mock git_module
    mock_git = mocker.patch('src.core.git_module.git_module')
    mock_git.create_branch.return_value = True
    mock_git.get_status.return_value = {"branch": "main"}
    
    # Test code that uses git_module
    result = work_module.create_work_item(db_session, "Test", "service", "new")
    
    # Verify mock was called
    mock_git.create_branch.assert_called_once()
```

### Best Practices

✅ **Arrange-Act-Assert Pattern**
```python
def test_something():
    # Arrange - Set up test data
    input_data = "test"
    
    # Act - Execute the code
    result = function_under_test(input_data)
    
    # Assert - Verify results
    assert result == expected
```

✅ **Descriptive Test Names**
```python
# Good
def test_create_work_item_generates_branch_name():
    ...

# Bad
def test_create():
    ...
```

✅ **One Assertion Focus**
```python
# Good - tests one thing
def test_validates_empty_title():
    success, msg = work_module.create_work_item(db, "", "service", "new")
    assert success is False

# Avoid - tests multiple things
def test_everything():
    # ... 50 lines of assertions ...
```

✅ **Test Edge Cases**
```python
def test_empty_input(db_session):
    result = module.process("")
    assert result is None

def test_none_input(db_session):
    result = module.process(None)
    assert result is None

def test_very_long_input(db_session):
    result = module.process("x" * 10000)
    assert len(result) <= 2000
```

---

## 🔗 Writing Integration Tests

Integration tests validate that modules work together correctly with real dependencies.

### Pattern: Integration Test with Real Git

```python
# tests/integration/test_workflows.py

import pytest
import tempfile
from pathlib import Path
import git
from src.core import work_module


@pytest.fixture
def temp_git_repo(monkeypatch):
    """Create temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize Git repo
        repo = git.Repo.init(tmpdir)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@test.com").release()
        
        # Create initial structure
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir()
        (docs_dir / "CHANGES.md").write_text("# Change Log\n\n")
        
        # Initial commit
        repo.index.add(["docs/CHANGES.md"])
        repo.index.commit("Initial commit")
        
        # Patch git_module to use temp repo
        import sys
        git_module_actual = sys.modules['src.core.git_module']
        work_module_actual = sys.modules['src.core.work_module']
        doc_module_actual = sys.modules['src.core.documentation_module']
        
        temp_git = git_module_actual.GitModule(tmpdir)
        temp_docs = doc_module_actual.DocumentationModule(
            docs_path="docs", 
            repo_path=tmpdir
        )
        
        # CRITICAL: Patch ALL references
        monkeypatch.setattr(git_module_actual, 'git_module', temp_git)
        monkeypatch.setattr(work_module_actual, 'git_module', temp_git)
        monkeypatch.setattr(doc_module_actual, 'documentation_module', temp_docs)
        monkeypatch.setattr(work_module_actual, 'documentation_module', temp_docs)
        
        yield tmpdir


@pytest.mark.integration
def test_full_workflow(db_session, temp_git_repo):
    """Test complete work item workflow with real Git."""
    # Create work item (creates Git branch)
    work = work_module.create_work_item(
        db_session,
        title="Integration Test Work",
        category="service",
        action_type="new"
    )
    
    # Verify Git branch created
    repo = git.Repo(temp_git_repo)
    branches = [b.name for b in repo.heads]
    assert work.git_branch in branches
    
    # Complete checklist
    for i in range(len(work.checklist)):
        work_module.toggle_checklist_item(db_session, work.id, i)
    
    # Create file and commit
    test_file = Path(temp_git_repo) / "test.txt"
    test_file.write_text("Test content")
    
    success, msg = work_module.commit_work(
        db_session,
        work.id,
        "Test commit",
        "Added test file"
    )
    assert success is True
    
    # Verify commit in Git
    commits = list(repo.iter_commits(work.git_branch))
    assert any("Test commit" in c.message for c in commits)
    
    # Merge and complete
    success, msg = work_module.merge_and_complete(db_session, work.id)
    assert success is True
    
    # Verify work completed
    db_session.refresh(work)
    assert work.status == "complete"
    assert work.branch_merged is True
```

### Critical Pattern: Fixture Patching

**Problem:** Python imports create references that don't get updated when you patch.

```python
# work_module.py does this at import time:
from .git_module import git_module  # Creates reference A

# Your test patches here:
monkeypatch.setattr(git_module, 'git_module', temp_git)  # Updates module
# But work_module still has reference A!
```

**Solution:** Patch BOTH the module AND the reference:

```python
# 1. Patch the module singleton
monkeypatch.setattr(git_module_actual, 'git_module', temp_git)

# 2. Patch work_module's reference (CRITICAL!)
monkeypatch.setattr(work_module_actual, 'git_module', temp_git)
```

### Integration Test Checklist

When writing integration tests:

- [ ] Use `@pytest.mark.integration` decorator
- [ ] Use real dependencies (Git, filesystem)
- [ ] Create isolated temporary directories
- [ ] Patch ALL module references (not just singletons)
- [ ] Clean up after test (use context managers/fixtures)
- [ ] Test complete workflows (not just single methods)
- [ ] Verify side effects (files created, commits made, DB updated)
- [ ] Use unique test data (UUIDs, timestamps) to avoid collisions

---

## 🎨 Testing Patterns

### Pattern 1: Testing Return Values

```python
@pytest.mark.unit
def test_returns_tuple(db_session):
    """Test method that returns (bool, str)."""
    success, message = module.do_action(db_session, "valid")
    
    assert success is True
    assert "success" in message.lower()

@pytest.mark.unit  
def test_returns_none_not_found(db_session):
    """Test method returns None when not found."""
    result = module.get_item(db_session, 99999)
    
    assert result is None
```

### Pattern 2: Testing Database Changes

```python
@pytest.mark.unit
def test_creates_database_record(db_session):
    """Test method creates database record."""
    # Before
    count_before = db_session.query(models.Item).count()
    
    # Act
    item = module.create_item(db_session, "Test")
    
    # After
    count_after = db_session.query(models.Item).count()
    assert count_after == count_before + 1
    assert item.id is not None

@pytest.mark.unit
def test_updates_existing_record(db_session):
    """Test method updates existing record."""
    # Create item
    item = models.Item(name="Original")
    db_session.add(item)
    db_session.commit()
    
    # Update
    module.update_item(db_session, item.id, name="Updated")
    
    # Verify
    db_session.refresh(item)
    assert item.name == "Updated"
```

### Pattern 3: Testing Validation

```python
@pytest.mark.unit
def test_validates_required_field(db_session):
    """Test validation rejects empty required field."""
    success, message = module.create_item(db_session, name="")
    
    assert success is False
    assert "required" in message.lower() or "empty" in message.lower()

@pytest.mark.unit
def test_validates_length(db_session):
    """Test validation enforces max length."""
    long_name = "x" * 1000
    success, message = module.create_item(db_session, name=long_name)
    
    assert success is False
    assert "long" in message.lower() or "length" in message.lower()
```

### Pattern 4: Testing with Mocks

```python
@pytest.mark.unit
def test_with_mocked_external_call(db_session, mocker):
    """Test with mocked external dependency."""
    # Mock the external module
    mock_external = mocker.patch('src.core.external_module.external_function')
    mock_external.return_value = "mocked_result"
    
    # Test your code
    result = module.do_something_that_calls_external(db_session)
    
    # Verify mock was called correctly
    mock_external.assert_called_once_with(expected_arg)
    assert result == "expected_based_on_mock"
```

### Pattern 5: Testing Error Handling

```python
@pytest.mark.unit
def test_handles_database_error(db_session, mocker):
    """Test graceful handling of database errors."""
    # Make database raise an error
    mocker.patch.object(db_session, 'commit', side_effect=Exception("DB Error"))
    
    # Should not raise, should return error
    success, message = module.create_item(db_session, "Test")
    
    assert success is False
    assert "error" in message.lower()

@pytest.mark.unit
def test_handles_not_found(db_session):
    """Test handling of non-existent items."""
    # Should not raise, should return False or None
    result = module.get_item(db_session, 99999)
    assert result is None
```

---

## 🚀 Test-Driven Development (TDD)

### TDD Cycle

1. **Red** - Write failing test
2. **Green** - Write minimal code to pass
3. **Refactor** - Clean up code

### Example TDD Workflow

```python
# Step 1: RED - Write failing test
def test_delete_work_item_removes_branch(db_session):
    """Test deleting work item deletes Git branch."""
    work = create_test_work_item(db_session)
    branch = work.git_branch
    
    module.delete_work_item(db_session, work.id)
    
    # This will fail - method doesn't exist yet
    assert branch not in get_git_branches()

# Step 2: GREEN - Implement minimal code
def delete_work_item(db, work_id):
    work = db.query(WorkItem).get(work_id)
    if work and work.git_branch:
        git_module.delete_branch(work.git_branch)
    db.delete(work)
    db.commit()
    return True, "Deleted"

# Step 3: REFACTOR - Clean up, add error handling
def delete_work_item(db, work_id):
    work = db.query(WorkItem).filter(WorkItem.id == work_id).first()
    if not work:
        return False, "Not found"
    
    try:
        if work.git_branch:
            git_module.checkout_branch("main")
            git_module.repo.delete_head(work.git_branch, force=True)
        
        db.delete(work)
        db.commit()
        return True, "Deleted successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

---

## 📈 Coverage Analysis

### View Coverage Report

```bash
# Terminal report
pytest tests/ --cov=src/core --cov-report=term-missing

# HTML report (detailed)
pytest tests/ --cov=src/core --cov-report=html
open htmlcov/index.html
```

### Understanding Coverage

**Coverage shows:**
- ✅ Lines executed during tests (green)
- ❌ Lines not executed (red)
- ⚠️ Partial branches (yellow)

**What to focus on:**
1. **Critical paths** - User-facing features
2. **Complex logic** - Multiple conditionals
3. **Data transformations** - Calculations, parsing
4. **Error handling** - Exception cases

**What to ignore:**
- Simple getters/setters
- Logging statements
- Defensive programming (impossible cases)
- Third-party library wrappers

### Coverage Thresholds

Set minimum coverage in `pytest.ini`:

```ini
[pytest]
addopts = --cov-fail-under=70
```

This will **fail the build** if coverage drops below 70%.

---

## 🔍 Debugging Tests

### Print Debugging

```python
def test_something(db_session):
    result = module.do_something(db_session, "test")
    
    # Print for debugging
    print(f"Result: {result}")
    print(f"DB state: {db_session.query(Model).all()}")
    
    assert result is not None
```

Run with `-s` to see prints:
```bash
pytest tests/unit/test_file.py::test_something -v -s
```

### Breakpoint Debugging

```python
def test_something(db_session):
    result = module.do_something(db_session, "test")
    
    import pdb; pdb.set_trace()  # Debugger stops here
    
    assert result is not None
```

### VS Code Debugging

Add to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Pytest: Current File",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${file}",
                "-v",
                "-s"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

---

## 🎓 Best Practices Summary

### DO ✅

- Test business logic thoroughly
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test edge cases and errors
- Use fixtures for common setup
- Mock external dependencies
- Keep tests fast (< 0.1s for unit tests)
- Test one thing per test
- Use integration tests for workflows
- Aim for 70%+ coverage

### DON'T ❌

- Test third-party libraries
- Test simple getters/setters
- Have multiple assertions for different concerns
- Make tests depend on each other
- Use production database
- Leave commented-out tests
- Test implementation details
- Chase 100% coverage
- Make tests slow
- Ignore failing tests

---

## 📚 Further Reading

### Internal Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [ARCHITECTURE_PATTERNS_GUIDE.md](ARCHITECTURE_PATTERNS_GUIDE.md) - Code patterns
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development workflow
- [DEVELOPER_QUICK_REFERENCE.md](DEVELOPER_QUICK_REFERENCE.md) - Quick reference

### External Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test Driven Development by Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) - Kent Beck
- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) - Michael Feathers

---

## 🎯 Quick Reference

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src/core --cov-report=term-missing

# Run only fast tests
pytest tests/unit/ -v

# Run specific test
pytest tests/unit/test_work_module.py::TestWorkModule::test_create_work_item -v

# Debug a test
pytest tests/unit/test_file.py::test_name -v -s

# Generate HTML coverage report
pytest tests/ --cov=src/core --cov-report=html

# Run and stop on first failure
pytest tests/ -v -x
```

---

**Last Updated:** November 25, 2025  
**Test Suite Version:** 49 tests, 72.63% coverage  
**Status:** Phase 3 Complete ✅