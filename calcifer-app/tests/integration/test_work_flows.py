"""
Integration tests for work_module

Tests workflows with REAL dependencies:
- Real Git repositories (temporary, isolated per test)
- Real file system operations
- Real database queries

These tests validate that work_module methods work correctly
when integrated with actual Git, filesystem, and database.
"""

import pytest
import tempfile
import shutil
import os
import git
from pathlib import Path
from src.core import work_module, documentation_module, git_module
from src import models


@pytest.fixture(scope="function", autouse=True)
def reset_git_module():
    """
    Reset git_module singleton between tests.
    
    This prevents branch conflicts when multiple tests
    create branches with the same name on the same date.
    """
    # Store original
    import sys
    git_module_actual = sys.modules['src.core.git_module']
    original = git_module_actual.git_module
    
    yield
    
    # Restore original after test
    git_module_actual.git_module = original


@pytest.fixture
def temp_git_repo(monkeypatch):
    """
    Create a FRESH temporary Git repository for each test.
    
    This fixture:
    - Creates a temporary directory
    - Initializes a Git repo
    - Patches git_module to use this repo
    - Cleans up after the test
    
    Each test gets a completely isolated Git environment.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize Git repo
        repo = git.Repo.init(tmpdir)
        
        # Configure Git user (required for commits)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Create docs directory
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create initial CHANGES.md
        changes_file = docs_dir / "CHANGES.md"
        changes_file.write_text("# Change Log\n\nAll changes logged here.\n\n")
        
        # Initial commit (Git needs at least one commit)
        repo.index.add(["docs/CHANGES.md"])
        repo.index.commit("Initial commit")
        
        # Patch git_module to use this temp repo
        import sys
        git_module_actual = sys.modules['src.core.git_module']
        
        # Create NEW GitModule instance for THIS test
        temp_git = git_module_actual.GitModule(tmpdir)
        monkeypatch.setattr(git_module_actual, 'git_module', temp_git)
        
        # Also patch documentation_module to use temp docs path
        doc_module_actual = sys.modules['src.core.documentation_module']
        temp_docs = doc_module_actual.DocumentationModule(docs_path="docs", repo_path=tmpdir)
        monkeypatch.setattr(doc_module_actual, 'documentation_module', temp_docs)
        
        yield tmpdir
        
        # Cleanup happens automatically


class TestWorkFlowsIntegration:
    """Integration tests for complete work item workflows."""
    
    @pytest.mark.integration
    def test_commit_work_with_real_git(self, db_session, temp_git_repo):
        """
        Test commit_work() with real Git operations.
        
        This validates:
        - Real Git branch checkout
        - Real file system writes (CHANGES.md)
        - Real Git commit creation
        - Database commit record creation
        """
        # Arrange - Create work item (creates real Git branch)
        work = work_module.create_work_item(
            db_session,
            title="Test Work Item",
            category="service",
            action_type="new",
            description="Integration test"
        )
        
        # Verify branch was created
        repo = git.Repo(temp_git_repo)
        branches = [b.name for b in repo.heads]
        assert work.git_branch in branches, f"Branch {work.git_branch} not found in {branches}"
        
        # Create a test file to commit
        test_file = Path(temp_git_repo) / "test_file.txt"
        test_file.write_text("Test content for commit")
        
        # Act - Commit changes
        success, message = work_module.commit_work(
            db_session,
            work.id,
            commit_message="Test commit message",
            changes_entry="Added test file for integration testing"
        )
        
        # Assert - Commit succeeded
        assert success is True
        assert "successfully" in message.lower()
        
        # Assert - Real Git commit was created
        commits = list(repo.iter_commits(work.git_branch, max_count=10))
        assert len(commits) >= 2  # Initial + our commit
        latest_commit = commits[0]
        assert "Test commit message" in latest_commit.message
        
        # Assert - CHANGES.md was updated
        changes_path = Path(temp_git_repo) / "docs" / "CHANGES.md"
        assert changes_path.exists()
        changes_content = changes_path.read_text()
        assert "Added test file for integration testing" in changes_content
        
        # Assert - Database commit record created
        db_commits = db_session.query(models.Commit).filter(
            models.Commit.work_item_id == work.id
        ).all()
        assert len(db_commits) == 1
        assert db_commits[0].commit_message == "Test commit message"
        assert db_commits[0].commit_sha is not None
    
    @pytest.mark.integration
    def test_commit_work_validates_inputs(self, db_session, temp_git_repo):
        """Test that commit_work validates required inputs."""
        # Arrange
        work = work_module.create_work_item(
            db_session, "Test Validation", "service", "new"
        )
        
        # Act & Assert - Empty commit message
        success, message = work_module.commit_work(
            db_session,
            work.id,
            commit_message="",
            changes_entry="Has entry"
        )
        assert success is False
        assert "message" in message.lower()
        
        # Act & Assert - Empty changes entry
        success, message = work_module.commit_work(
            db_session,
            work.id,
            commit_message="Has message",
            changes_entry=""
        )
        assert success is False
        assert "changes" in message.lower() or "entry" in message.lower()


class TestMergeAndCompleteIntegration:
    """Integration tests for merge_and_complete workflow."""
    
    @pytest.mark.integration
    def test_merge_and_complete_full_workflow(self, db_session, temp_git_repo):
        """
        Test complete merge and complete workflow.
        
        This validates:
        - Checklist completion validation
        - CHANGES.md validation
        - Real Git merge to main
        - Work item status update
        """
        # Arrange - Create work item
        work = work_module.create_work_item(
            db_session,
            title="Complete Work",
            category="service",
            action_type="new"
        )
        
        # Complete all checklist items
        for i in range(len(work.checklist)):
            work_module.toggle_checklist_item(db_session, work.id, i)
        
        # Create and commit a change (required for merge)
        test_file = Path(temp_git_repo) / "completed_work.txt"
        test_file.write_text("Work is done!")
        
        success, msg = work_module.commit_work(
            db_session,
            work.id,
            "Complete the work",
            "Finished all tasks"
        )
        assert success is True, f"Commit failed: {msg}"
        
        # Act - Merge and complete
        success, message = work_module.merge_and_complete(db_session, work.id)
        
        # Assert - Success
        assert success is True, f"Merge failed: {message}"
        assert "successfully" in message.lower()
        
        # Assert - Work item marked complete
        db_session.refresh(work)
        assert work.status == "complete"
        assert work.completed_date is not None
        assert work.branch_merged is True
        
        # Assert - Branch actually merged in Git
        repo = git.Repo(temp_git_repo)
        assert repo.active_branch.name == "main"  # Should be back on main
        
        # Verify merge happened by checking main has the commit
        main_commits = list(repo.iter_commits("main"))
        commit_messages = [c.message for c in main_commits]
        assert any("Complete the work" in msg for msg in commit_messages)
    
    @pytest.mark.integration
    def test_merge_and_complete_fails_incomplete_checklist(self, db_session, temp_git_repo):
        """Test that merge fails if checklist incomplete."""
        # Arrange - Create work with incomplete checklist
        work = work_module.create_work_item(
            db_session, "Incomplete Checklist", "service", "new"
        )
        
        # Add commit (but leave checklist incomplete)
        test_file = Path(temp_git_repo) / "test.txt"
        test_file.write_text("Content")
        work_module.commit_work(
            db_session, work.id, "Test", "Test entry"
        )
        
        # Act
        success, message = work_module.merge_and_complete(db_session, work.id)
        
        # Assert - Should fail
        assert success is False
        assert "checklist" in message.lower()


class TestWorkDetailIntegration:
    """Integration tests for aggregation methods."""
    
    @pytest.mark.integration
    def test_get_work_detail_with_real_data(self, db_session, temp_git_repo):
        """
        Test get_work_detail() with real database queries and Git data.
        
        This validates:
        - Real database joins
        - Real Git branch queries
        - Correct data aggregation
        """
        # Arrange - Create work item
        work = work_module.create_work_item(
            db_session,
            title="Detail Test Work",
            category="service",
            action_type="new"
        )
        
        # Add a commit
        test_file = Path(temp_git_repo) / "detail_test.txt"
        test_file.write_text("Content")
        work_module.commit_work(
            db_session,
            work.id,
            "Test commit for detail",
            "Test entry for detail"
        )
        
        # Act
        result = work_module.get_work_detail(db_session, work.id)
        
        # Assert - Returns complete data structure
        assert result is not None
        assert "work_item" in result
        assert "commits" in result
        assert "branch_commits" in result
        assert "branch_merged" in result
        
        # Assert - Work item data correct
        assert result["work_item"].id == work.id
        assert result["work_item"].title == "Detail Test Work"
        
        # Assert - Commits included
        assert len(result["commits"]) == 1
        assert result["commits"][0].commit_message == "Test commit for detail"
        
        # Assert - Branch commits from Git
        assert len(result["branch_commits"]) >= 1
        
        # Assert - Merge status
        assert result["branch_merged"] is False  # Not merged yet
    
    @pytest.mark.integration
    def test_get_work_detail_nonexistent(self, db_session, temp_git_repo):
        """Test get_work_detail with non-existent work item."""
        # Act
        result = work_module.get_work_detail(db_session, 99999)
        
        # Assert
        assert result is None
    
    @pytest.mark.integration
    def test_get_dashboard_data(self, db_session, temp_git_repo):
        """
        Test get_dashboard_data() with real queries.
        
        This validates:
        - Multiple real database queries
        - Data aggregation from multiple tables
        - Git status integration
        """
        # Arrange - Create mix of work items
        active1 = work_module.create_work_item(
            db_session, "Active Work 1", "service", "new"
        )
        active2 = work_module.create_work_item(
            db_session, "Active Work 2", "platform_feature", "change"
        )
        
        # Complete one work item
        completed = work_module.create_work_item(
            db_session, "Completed Work", "service", "fix"
        )
        for i in range(len(completed.checklist)):
            work_module.toggle_checklist_item(db_session, completed.id, i)
        
        # Commit something
        test_file = Path(temp_git_repo) / "dashboard_test.txt"
        test_file.write_text("Content")
        work_module.commit_work(
            db_session, completed.id, "Complete", "Finished"
        )
        work_module.merge_and_complete(db_session, completed.id)
        
        # Act
        result = work_module.get_dashboard_data(db_session)
        
        # Assert - All expected keys present
        assert "active_work" in result
        assert "completed_work" in result
        assert "recent_changes" in result
        assert "git_status" in result
        
        # Assert - Active work includes our items
        active_ids = [w.id for w in result["active_work"]]
        assert active1.id in active_ids
        assert active2.id in active_ids
        assert completed.id not in active_ids  # Completed, not active
        
        # Assert - Completed work includes completed item
        completed_ids = [w.id for w in result["completed_work"]]
        assert completed.id in completed_ids
        
        # Assert - Git status is real
        assert "branch" in result["git_status"]
        assert result["git_status"]["branch"] == "main"  # After merge


class TestWorkDeletionIntegration:
    """Integration tests for work item deletion with Git cleanup."""
    
    @pytest.mark.integration
    def test_delete_work_item_removes_git_branch(self, db_session, temp_git_repo):
        """
        Test that deleting work item also deletes Git branch.
        
        This validates:
        - Database deletion
        - Git branch cleanup
        - Proper cleanup of Git resources
        """
        # Arrange - Create work item (creates Git branch)
        work = work_module.create_work_item(
            db_session,
            title="Work To Delete",
            category="service",
            action_type="new"
        )
        
        branch_name = work.git_branch
        work_id = work.id
        
        # Verify branch exists
        repo = git.Repo(temp_git_repo)
        branches_before = [b.name for b in repo.heads]
        assert branch_name in branches_before, f"Branch {branch_name} not found in {branches_before}"
        
        # Act - Delete work item
        success, message = work_module.delete_work_item(db_session, work_id)
        
        # Assert - Deletion succeeded
        assert success is True
        assert "success" in message.lower()
        
        # Assert - Work item removed from database
        deleted_work = db_session.query(models.WorkItem).filter(
            models.WorkItem.id == work_id
        ).first()
        assert deleted_work is None
        
        # Assert - Git branch also deleted
        branches_after = [b.name for b in repo.heads]
        assert branch_name not in branches_after, f"Branch {branch_name} still exists in {branches_after}"
        
        # Assert - Currently on main branch (not deleted branch)
        assert repo.active_branch.name == "main"


# Performance/Stress Tests (marked as slow)

class TestWorkFlowsPerformance:
    """Performance tests for work item workflows."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_create_multiple_work_items(self, db_session, temp_git_repo):
        """Test creating multiple work items rapidly."""
        # Arrange
        count = 10
        
        # Act - Create multiple work items
        work_items = []
        for i in range(count):
            work = work_module.create_work_item(
                db_session,
                title=f"Work Item Number {i}",  # Make titles unique
                category="service",
                action_type="new"
            )
            work_items.append(work)
        
        # Assert - All created successfully
        assert len(work_items) == count
        
        # Assert - All have unique branches
        branch_names = [w.git_branch for w in work_items]
        assert len(set(branch_names)) == count  # All unique
        
        # Assert - All branches exist in Git
        repo = git.Repo(temp_git_repo)
        git_branches = [b.name for b in repo.heads]
        for branch_name in branch_names:
            assert branch_name in git_branches, f"Branch {branch_name} not in {git_branches}"