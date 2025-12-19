"""
Pytest Configuration and Shared Fixtures

Fixtures defined here are available to all tests.
"""

import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import git

import src.core.work_module
from src.database import Base
from src import models


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """
    Create in-memory SQLite database engine.
    
    Scope: function (new database for each test)
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Create database session for tests.
    
    Automatically rolls back changes after each test.
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_work_item(db_session):
    """Create a sample work item for testing."""
    work = models.WorkItem(
        title="Test Work Item",
        category="service",
        action_type="new",
        description="Test description",
        git_branch="service/new/test-work-20251124",
        status="planning",
        checklist=[
            {"item": "Task 1", "done": False},
            {"item": "Task 2", "done": False},
            {"item": "Task 3", "done": False}
        ]
    )
    db_session.add(work)
    db_session.commit()
    db_session.refresh(work)
    return work


@pytest.fixture
def sample_service(db_session):
    """Create a sample service for testing."""
    service = models.Service(
        name="Test Service",
        service_type="container",
        host="test-host",
        url="http://test.local",
        description="Test service description",
        status="active"
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def sample_endpoint(db_session):
    """Create a sample endpoint for testing."""
    endpoint = models.Endpoint(
        name="Test Endpoint",
        endpoint_type="network",
        target="127.0.0.1",
        check_interval=60,
        status="unknown"
    )
    db_session.add(endpoint)
    db_session.commit()
    db_session.refresh(endpoint)
    return endpoint


# ============================================================================
# GIT FIXTURES
# ============================================================================

@pytest.fixture
def temp_git_repo(tmp_path):
    """
    Create temporary Git repository for testing.
    
    Automatically cleaned up after test.
    """
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize repo
    repo = git.Repo.init(repo_path)
    
    # Configure repo
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
    
    # Create initial commit
    readme = repo_path / "README.md"
    readme.write_text("# Test Repo\n")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")
    
    # Create docs directory with CHANGES.md
    docs_path = repo_path / "docs"
    docs_path.mkdir()
    changes = docs_path / "CHANGES.md"
    changes.write_text("# Change Log\n\nAll changes logged here.\n\n")
    repo.index.add(["docs/CHANGES.md"])
    repo.index.commit("Add CHANGES.md")
    
    yield repo_path
    
    # Cleanup handled automatically by tmp_path

# Add this BEFORE the mock_git fixture (around line 160)
import sys
print("=" * 80)
print("PYTHON PATH:")
for p in sys.path:
    print(f"  {p}")
print("=" * 80)

# Try importing to see what we get
try:
    import src.core.work_module as wm
    print(f"work_module imported: {wm}")
    print(f"work_module.__file__: {wm.__file__}")
    print(f"git_module in work_module namespace: {hasattr(wm, 'git_module')}")
    print(f"work_module.__dict__ keys: {list(wm.__dict__.keys())}")
    print("=" * 80)
except Exception as e:
    print(f"ERROR importing: {e}")
    print("=" * 80)

@pytest.fixture
def mock_git(monkeypatch):
    """
    Mock Git module for unit tests.
    
    Prevents actual Git operations during unit tests.
    """
    mock = MagicMock()
    
    # Configure mock methods with realistic return values
    mock.create_branch.return_value = True
    mock.checkout_branch.return_value = True
    mock.get_branches.return_value = ["main", "test-branch"]
    mock.get_current_branch.return_value = "main"
    mock.get_status.return_value = {
        "branch": "main",
        "is_dirty": False,
        "untracked_files": [],
        "modified_files": [],
        "staged_files": []
    }
    mock.stage_files.return_value = True
    mock.commit.return_value = "abc123def456"
    mock.is_branch_merged.return_value = False
    mock.merge_branch.return_value = (True, "merged_sha")
    mock.generate_branch_name.side_effect = lambda cat, act, title: f"{cat}/{act}/{title.lower().replace(' ', '-')}"
    mock.get_branch_commits.return_value = []
    mock.check_changes_md_updated.return_value = True
    
    # Mock the repo attribute that delete_work_item uses
    mock.repo = MagicMock()
    mock.repo.delete_head = MagicMock()
    
    # CRITICAL: Import the MODULE (not the class/singleton)
    # We need to patch at the module level where git_module is imported
    import sys
    work_module_actual = sys.modules['src.core.work_module']
    
    # Patch the git_module name in the work_module's namespace
    monkeypatch.setattr(work_module_actual, 'git_module', mock)
    
    return mock

# ============================================================================
# INTEGRATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_monitoring(monkeypatch):
    """Mock monitoring integration for unit tests."""
    mock = MagicMock()
    
    # Configure mock methods
    mock.check_endpoint.return_value = (True, None)
    mock.update_endpoint_status.return_value = True
    mock.generate_endpoint_documentation.return_value = "# Test Doc\n"
    
    # Replace monitoring with mock
    monkeypatch.setattr(
        'src.integrations.monitoring.endpoint_module.monitoring',
        mock
    )
    
    return mock