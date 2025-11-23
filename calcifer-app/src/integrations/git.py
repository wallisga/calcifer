"""
Git Integration

Provides Git repository operations and branch management.
This is an integration rather than core feature - Calcifer can work without it,
but Git integration enables automatic branch management and change tracking.
"""

import git
import os
from datetime import datetime
from typing import Optional, List, Tuple, Dict


class GitIntegration:
    """
    Git integration for Calcifer.
    
    Manages Git operations for the infrastructure repository including:
    - Branch creation and management
    - Commit operations
    - Merge operations
    - Branch status tracking
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git integration.
        
        Args:
            repo_path: Path to Git repository
        """
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            # If not a repo, initialize it
            self.repo = git.Repo.init(repo_path)
    
    def check_connectivity(self) -> bool:
        """
        Test if Git integration is working.
        
        Returns:
            True if Git repository is accessible
        """
        try:
            _ = self.repo.git_dir
            return True
        except:
            return False
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return self.repo.active_branch.name
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create a new branch and optionally check it out.
        
        Args:
            branch_name: Name of the branch to create
            checkout: Whether to checkout the new branch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return True
        except git.GitCommandError as e:
            print(f"Error creating branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.repo.git.checkout(branch_name)
            return True
        except git.GitCommandError as e:
            print(f"Error checking out branch: {e}")
            return False
    
    def get_branches(self) -> List[str]:
        """Get list of all branches."""
        return [head.name for head in self.repo.heads]
    
    def delete_branch(self, branch_name: str, force: bool = False) -> bool:
        """
        Delete a local branch.
        
        Args:
            branch_name: Name of the branch to delete
            force: Whether to force delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Can't delete current branch, switch to main first
            if self.get_current_branch() == branch_name:
                self.checkout_branch("main")
            
            self.repo.delete_head(branch_name, force=force)
            
            # Try to delete remote branch if it exists
            try:
                self.repo.git.push('origin', '--delete', branch_name)
            except:
                pass  # Remote branch might not exist
            
            return True
        except git.GitCommandError as e:
            print(f"Error deleting branch: {e}")
            return False
    
    def get_status(self) -> Dict[str, any]:
        """
        Get repository status.
        
        Returns:
            Dict with branch, is_dirty, and file lists
        """
        return {
            "branch": self.get_current_branch(),
            "is_dirty": self.repo.is_dirty(),
            "untracked_files": self.repo.untracked_files,
            "modified_files": [item.a_path for item in self.repo.index.diff(None)],
            "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")]
        }
    
    def stage_files(self, files: List[str]) -> bool:
        """
        Stage files for commit.
        
        Args:
            files: List of file paths to stage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.repo.index.add(files)
            return True
        except git.GitCommandError as e:
            print(f"Error staging files: {e}")
            return False
    
    def stage_all(self) -> bool:
        """
        Stage all changes (git add -A).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.repo.git.add('-A')
            return True
        except git.GitCommandError as e:
            print(f"Error staging all files: {e}")
            return False
    
    def commit(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None
    ) -> Optional[str]:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            author_name: Optional author name (uses git config if not provided)
            author_email: Optional author email
            
        Returns:
            Commit SHA if successful, None otherwise
        """
        try:
            if author_name and author_email:
                author = git.Actor(author_name, author_email)
                commit = self.repo.index.commit(message, author=author)
            else:
                commit = self.repo.index.commit(message)
            return commit.hexsha
        except git.GitCommandError as e:
            print(f"Error committing: {e}")
            return None
    
    def get_recent_commits(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Get recent commits.
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dicts
        """
        commits = []
        for commit in self.repo.iter_commits(max_count=limit):
            commits.append({
                "sha": commit.hexsha[:7],
                "full_sha": commit.hexsha,
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": datetime.fromtimestamp(commit.committed_date)
            })
        return commits
    
    def get_branch_commits(
        self,
        branch_name: str,
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """
        Get commits from a specific branch (not in main).
        
        Args:
            branch_name: Name of the branch
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dicts
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(f'main..{branch_name}', max_count=limit):
                commits.append({
                    "sha": commit.hexsha[:7],
                    "full_sha": commit.hexsha,
                    "message": commit.message.strip().split('\n')[0],
                    "author": commit.author.name,
                    "date": datetime.fromtimestamp(commit.committed_date),
                    "full_message": commit.message.strip()
                })
            return commits
        except git.GitCommandError:
            return []
    
    def is_branch_merged(
        self,
        branch_name: str,
        target_branch: str = "main"
    ) -> bool:
        """
        Check if a branch has been merged into target branch.
        
        Args:
            branch_name: Branch to check
            target_branch: Target branch (usually 'main')
            
        Returns:
            True if merged, False otherwise
        """
        try:
            commits = list(self.repo.iter_commits(f'{target_branch}..{branch_name}'))
            return len(commits) == 0
        except git.GitCommandError:
            return False
    
    def get_branch_info(self, branch_name: str) -> Dict[str, any]:
        """
        Get information about a branch.
        
        Args:
            branch_name: Name of the branch
            
        Returns:
            Dict with branch information or {"exists": False}
        """
        try:
            branch = self.repo.heads[branch_name]
            return {
                "exists": True,
                "commit_sha": branch.commit.hexsha[:7],
                "full_commit_sha": branch.commit.hexsha,
                "commit_message": branch.commit.message.strip(),
                "author": branch.commit.author.name,
                "date": datetime.fromtimestamp(branch.commit.committed_date)
            }
        except (IndexError, AttributeError):
            return {"exists": False}
    
    def merge_branch(
        self,
        branch_name: str,
        target_branch: str = "main"
    ) -> Tuple[bool, str]:
        """
        Merge a branch into target branch.
        
        Args:
            branch_name: Branch to merge
            target_branch: Target branch to merge into
            
        Returns:
            Tuple of (success, result_message)
        """
        try:
            # Checkout target branch
            self.checkout_branch(target_branch)
            
            # Merge the branch
            self.repo.git.merge(branch_name)
            
            # Get merge commit SHA
            merge_sha = self.repo.head.commit.hexsha
            
            return True, merge_sha
        except git.GitCommandError as e:
            return False, str(e)
    
    def check_changes_md_updated(self, branch_name: str = None) -> bool:
        """
        Check if CHANGES.md was modified in current branch compared to main.
        
        Args:
            branch_name: Optional branch name (uses current branch if not provided)
            
        Returns:
            True if CHANGES.md was modified, False otherwise
        """
        try:
            if branch_name:
                diff = self.repo.git.diff(f'main..{branch_name}', '--name-only')
            else:
                diff = self.repo.git.diff('main', '--name-only')
            return 'docs/CHANGES.md' in diff
        except git.GitCommandError:
            return False
    
    def validate_for_commit(self) -> Tuple[bool, str]:
        """
        Validate repository is ready for commit.
        
        Returns:
            Tuple of (is_valid, message)
        """
        # Check if there are staged changes
        if not self.repo.index.diff("HEAD"):
            return False, "No staged changes to commit"
        
        # Check if CHANGES.md is staged
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        if "docs/CHANGES.md" not in staged_files:
            return False, "docs/CHANGES.md must be updated and staged before committing"
        
        return True, "Ready to commit"
    
    def get_author_info(self) -> Tuple[str, str]:
        """
        Get Git author information from config.
        
        Returns:
            Tuple of (author_name, author_email)
        """
        try:
            name = self.repo.config_reader().get_value("user", "name")
            email = self.repo.config_reader().get_value("user", "email")
            return name, email
        except:
            return "Unknown", ""


# Singleton instance for easy import
git_integration = GitIntegration()