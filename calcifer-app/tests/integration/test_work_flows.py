"""
Integration tests for work_module - ACTUALLY WORKING VERSION.

Key fix: Patch BOTH the module singleton AND work_module's reference to it.
"""

import pytest
import tempfile
import uuid
from pathlib import Path
import git
from datetime import datetime
from src.core import work_module, documentation_module, git_module
from src import models


@pytest.fixture
def temp_git_repo(monkeypatch):
    """
    Create a FRESH temporary Git repository for each test.
    
    CRITICAL: We must patch THREE places:
    1. git_module.git_module (the singleton)
    2. work_module's reference to git_module
    3. documentation_module.documentation_module
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize Git repo
        repo = git.Repo.init(tmpdir)
        
        # Configure Git user
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Create docs directory
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create initial CHANGES.md
        changes_file = docs_dir / "CHANGES.md"
        changes_file.write_text("# Change Log\n\nAll changes logged here.\n\n")
        
        # Initial commit
        repo.index.add(["docs/CHANGES.md"])
        repo.index.commit("Initial commit")
        
        # Import the actual module objects
        import sys
        git_module_actual = sys.modules['src.core.git_module']
        work_module_actual = sys.modules['src.core.work_module']
        doc_module_actual = sys.modules['src.core.documentation_module']
        
        # Create new instances pointing to temp repo
        temp_git = git_module_actual.GitModule(tmpdir)
        temp_docs = doc_module_actual.DocumentationModule(docs_path="docs", repo_path=tmpdir)
        
        # Patch ALL the places!
        # 1. The git_module singleton itself
        monkeypatch.setattr(git_module_actual, 'git_module', temp_git)
        
        # 2. work_module's reference to git_module (this is the KEY!)
        monkeypatch.setattr(work_module_actual, 'git_module', temp_git)
        
        # 3. documentation_module singleton
        monkeypatch.setattr(doc_module_actual, 'documentation_module', temp_docs)
        
        # 4. work_module's reference to documentation_module (CRITICAL!)
        monkeypatch.setattr(work_module_actual, 'documentation_module', temp_docs)
        
        yield tmpdir
        
        # Cleanup automatic


class TestWorkFlowsIntegration:
    """Integration tests for work item workflows."""
    
    @pytest.mark.integration
    def test_commit_work_with_real_git(self, db_session, temp_git_repo):
        """Test commit_work() with real Git operations."""
        # Create work item
        work = work_module.create_work_item(
            db_session,
            title=f"Test Work {uuid.uuid4().hex[:8]}",  # Unique title!
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
        
        # Commit changes
        success, message = work_module.commit_work(
            db_session,
            work.id,
            commit_message="Test commit message",
            changes_entry="Added test file for integration testing"
        )
        
        # Assertions
        assert success is True
        assert "successfully" in message.lower()
        
        # Verify Git commit created
        commits = list(repo.iter_commits(work.git_branch, max_count=10))
        assert len(commits) >= 2  # Initial + our commit
        assert "Test commit message" in commits[0].message
        
        # Verify CHANGES.md updated
        changes_path = Path(temp_git_repo) / "docs" / "CHANGES.md"
        assert "Added test file for integration testing" in changes_path.read_text()
        
        # Verify database commit record
        db_commits = db_session.query(models.Commit).filter(
            models.Commit.work_item_id == work.id
        ).all()
        assert len(db_commits) == 1
        assert db_commits[0].commit_message == "Test commit message"
    
    @pytest.mark.integration
    def test_commit_work_validates_inputs(self, db_session, temp_git_repo):
        """Test commit_work validates required inputs."""
        work = work_module.create_work_item(
            db_session, f"Validation Test {uuid.uuid4().hex[:8]}", "service", "new"
        )
        
        # Empty commit message
        success, message = work_module.commit_work(
            db_session, work.id, commit_message="", changes_entry="Has entry"
        )
        assert success is False
        assert "message" in message.lower()
        
        # Empty changes entry
        success, message = work_module.commit_work(
            db_session, work.id, commit_message="Has message", changes_entry=""
        )
        assert success is False
        assert "changes" in message.lower() or "entry" in message.lower()


class TestMergeAndCompleteIntegration:
    """Integration tests for merge_and_complete workflow."""
    
    @pytest.mark.integration
    def test_merge_and_complete_full_workflow(self, db_session, temp_git_repo):
        """Test complete merge workflow."""
        # Create work item
        work = work_module.create_work_item(
            db_session,
            title=f"Complete Work {uuid.uuid4().hex[:8]}",
            category="service",
            action_type="new"
        )
        
        # Complete checklist
        for i in range(len(work.checklist)):
            work_module.toggle_checklist_item(db_session, work.id, i)
        
        # Create and commit a change
        test_file = Path(temp_git_repo) / "completed_work.txt"
        test_file.write_text("Work is done!")
        
        success, msg = work_module.commit_work(
            db_session, work.id, "Complete the work", "Finished all tasks"
        )
        assert success is True, f"Commit failed: {msg}"
        
        # Merge and complete
        success, message = work_module.merge_and_complete(db_session, work.id)
        
        # Assertions
        assert success is True, f"Merge failed: {message}"
        assert "successfully" in message.lower()
        
        db_session.refresh(work)
        assert work.status == "complete"
        assert work.completed_date is not None
        assert work.branch_merged is True
        
        # Verify Git merge
        repo = git.Repo(temp_git_repo)
        assert repo.active_branch.name == "main"
        
        main_commits = list(repo.iter_commits("main"))
        commit_messages = [c.message for c in main_commits]
        assert any("Complete the work" in msg for msg in commit_messages)
    
    @pytest.mark.integration
    def test_merge_and_complete_fails_incomplete_checklist(self, db_session, temp_git_repo):
        """Test merge fails if checklist incomplete."""
        work = work_module.create_work_item(
            db_session, f"Incomplete {uuid.uuid4().hex[:8]}", "service", "new"
        )
        
        # Add commit but leave checklist incomplete
        test_file = Path(temp_git_repo) / "test.txt"
        test_file.write_text("Content")
        work_module.commit_work(db_session, work.id, "Test", "Test entry")
        
        # Try to merge
        success, message = work_module.merge_and_complete(db_session, work.id)
        
        # Should fail
        assert success is False
        assert "checklist" in message.lower()


class TestWorkDetailIntegration:
    """Integration tests for aggregation methods."""
    
    @pytest.mark.integration
    def test_get_work_detail_with_real_data(self, db_session, temp_git_repo):
        """Test get_work_detail() with real data."""
        # Create work item
        work = work_module.create_work_item(
            db_session,
            title=f"Detail Test {uuid.uuid4().hex[:8]}",
            category="service",
            action_type="new"
        )
        
        # Add a commit
        test_file = Path(temp_git_repo) / "detail_test.txt"
        test_file.write_text("Content")
        work_module.commit_work(
            db_session, work.id, "Test commit for detail", "Test entry for detail"
        )
        
        # Get detail
        result = work_module.get_work_detail(db_session, work.id)
        
        # Assertions
        assert result is not None
        assert "work_item" in result
        assert "commits" in result
        assert "branch_commits" in result
        assert "branch_merged" in result
        
        assert result["work_item"].id == work.id
        assert len(result["commits"]) == 1
        assert result["commits"][0].commit_message == "Test commit for detail"
        assert len(result["branch_commits"]) >= 1
        assert result["branch_merged"] is False
    
    @pytest.mark.integration
    def test_get_work_detail_nonexistent(self, db_session, temp_git_repo):
        """Test get_work_detail with non-existent work item."""
        result = work_module.get_work_detail(db_session, 99999)
        assert result is None
    
    @pytest.mark.integration
    def test_get_dashboard_data(self, db_session, temp_git_repo):
        """Test get_dashboard_data() with real queries."""
        # Create mix of work items
        active1 = work_module.create_work_item(
            db_session, f"Active 1 {uuid.uuid4().hex[:8]}", "service", "new"
        )
        active2 = work_module.create_work_item(
            db_session, f"Active 2 {uuid.uuid4().hex[:8]}", "platform_feature", "change"
        )
        
        # Complete one work item
        completed = work_module.create_work_item(
            db_session, f"Completed {uuid.uuid4().hex[:8]}", "service", "fix"
        )
        for i in range(len(completed.checklist)):
            work_module.toggle_checklist_item(db_session, completed.id, i)
        
        # Commit and complete
        test_file = Path(temp_git_repo) / "dashboard_test.txt"
        test_file.write_text("Content")
        work_module.commit_work(db_session, completed.id, "Complete", "Finished")
        success, _ = work_module.merge_and_complete(db_session, completed.id)
        assert success, "Merge should succeed"
        
        # Force refresh from database
        db_session.expire_all()
        db_session.commit()  # Ensure changes are flushed
        
        # Get dashboard data
        result = work_module.get_dashboard_data(db_session)
        
        # Assertions
        assert "active_work" in result
        assert "completed_work" in result
        assert "recent_changes" in result
        assert "git_status" in result
        
        active_ids = [w.id for w in result["active_work"]]
        assert active1.id in active_ids
        assert active2.id in active_ids
        assert completed.id not in active_ids
        
        completed_ids = [w.id for w in result["completed_work"]]
        assert completed.id in completed_ids
        
        assert "branch" in result["git_status"]
        assert result["git_status"]["branch"] == "main"


class TestWorkDeletionIntegration:
    """Integration tests for work item deletion."""
    
    @pytest.mark.integration
    def test_delete_work_item_removes_git_branch(self, db_session, temp_git_repo):
        """Test deleting work item deletes Git branch."""
        # Create work item
        work = work_module.create_work_item(
            db_session,
            title=f"To Delete {uuid.uuid4().hex[:8]}",
            category="service",
            action_type="new"
        )
        
        branch_name = work.git_branch
        work_id = work.id
        
        # Verify branch exists
        repo = git.Repo(temp_git_repo)
        branches_before = [b.name for b in repo.heads]
        assert branch_name in branches_before, f"Branch {branch_name} not found in {branches_before}"
        
        # Delete work item
        success, message = work_module.delete_work_item(db_session, work_id)
        
        # Assertions
        assert success is True
        assert "success" in message.lower()
        
        # Verify database deletion
        deleted_work = db_session.query(models.WorkItem).filter(
            models.WorkItem.id == work_id
        ).first()
        assert deleted_work is None
        
        # Verify Git branch deleted
        branches_after = [b.name for b in repo.heads]
        assert branch_name not in branches_after, f"Branch {branch_name} still in {branches_after}"
        assert repo.active_branch.name == "main"


class TestWorkFlowsPerformance:
    """Performance tests."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_create_multiple_work_items(self, db_session, temp_git_repo):
        """Test creating multiple work items rapidly."""
        count = 10
        
        # Create multiple work items with UNIQUE titles
        work_items = []
        for i in range(count):
            work = work_module.create_work_item(
                db_session,
                title=f"Item {i} {uuid.uuid4().hex[:8]}",  # Guaranteed unique!
                category="service",
                action_type="new"
            )
            work_items.append(work)
        
        # Assertions
        assert len(work_items) == count
        
        # All have unique branches
        branch_names = [w.git_branch for w in work_items]
        assert len(set(branch_names)) == count
        
        # All branches exist in Git
        repo = git.Repo(temp_git_repo)
        git_branches = [b.name for b in repo.heads]
        for branch_name in branch_names:
            assert branch_name in git_branches, f"Branch {branch_name} not in {git_branches}"