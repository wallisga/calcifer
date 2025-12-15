"""
Core Git Module

Handles LOCAL Git operations required for work item workflow.
This is CORE functionality - required for Calcifer to work.

Remote operations (push, pull, PRs) belong in integrations/git_remote.
"""

import git
import os
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path

from .logging_module import get_logger

logger = get_logger('calcifer.core.git')

# Define directory paths for singleton
module_dir = Path(__file__).resolve().parent  # .../src/core/
src_dir = module_dir.parent                    # .../src/
app_dir = src_dir.parent                       # .../calcifer-app/
repo_path = str(app_dir)               

class GitModule:
    """
    Local Git operations for work item workflow.
    
    This module handles all local Git operations needed for the core
    Calcifer workflow: creating branches, committing changes, merging.
    
    Remote operations (push/pull/PR) are NOT in this module - they
    belong in the optional git_remote integration.
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize Git module with repository path.
        
        Args:
            repo_path: Path to Git repository (default: current directory)
        """
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            # If not a repo, initialize it
            self.repo = git.Repo.init(repo_path)
    
    # ========================================================================
    # BRANCH OPERATIONS
    # ========================================================================
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return self.repo.active_branch.name
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create a new branch and optionally check it out.
        
        Args:
            branch_name: Name of the branch to create
            checkout: Whether to checkout the branch after creating
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return True
        except git.GitCommandError as e:
            logger.error(f"Error creating branch: {e}", exc_info=True)
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
            logger.error(f"Error checking out branch: {e}", exc_info=True)
            return False
    
    def get_branches(self) -> List[str]:
        """Get list of all local branches."""
        return [head.name for head in self.repo.heads]
    
    def is_branch_merged(self, branch_name: str, target_branch: str = "main") -> bool:
        """
        Check if a branch has been merged into target branch.
        
        Args:
            branch_name: Name of the branch to check
            target_branch: Target branch (default: main)
            
        Returns:
            True if merged, False otherwise
        """
        try:
            # Get commits in branch but not in target
            commits = list(self.repo.iter_commits(f'{target_branch}..{branch_name}'))
            # If no commits, branch is merged (or never had unique commits)
            return len(commits) == 0
        except git.GitCommandError:
            return False
    
    def get_branch_info(self, branch_name: str) -> dict:
        """
        Get information about a branch.
        
        Args:
            branch_name: Name of the branch
            
        Returns:
            Dictionary with branch information or {"exists": False}
        """
        try:
            branch = self.repo.heads[branch_name]
            return {
                "exists": True,
                "commit_sha": branch.commit.hexsha[:7],
                "commit_message": branch.commit.message.strip(),
                "author": branch.commit.author.name,
                "date": datetime.fromtimestamp(branch.commit.committed_date)
            }
        except (IndexError, AttributeError):
            return {"exists": False}
    
    def get_branch_commits(self, branch_name: str, limit: int = 20) -> List[dict]:
        """
        Get commits from a specific branch (not in main).
        
        Args:
            branch_name: Name of the branch
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(f'main..{branch_name}', max_count=limit):
                commits.append({
                    "sha": commit.hexsha[:7],
                    "message": commit.message.strip().split('\n')[0],  # First line only
                    "author": commit.author.name,
                    "date": datetime.fromtimestamp(commit.committed_date),
                    "full_message": commit.message.strip()
                })
            return commits
        except git.GitCommandError:
            return []
    
    # ========================================================================
    # COMMIT OPERATIONS
    # ========================================================================
    
    def get_status(self) -> dict:
        """Get repository status."""
        # Handle case where repo has no commits yet (no HEAD)
        try:
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        except:
            staged_files = []
        
        try:
            current_branch = self.get_current_branch()
        except:
            current_branch = "main"
        
        return {
            "branch": current_branch,
            "is_dirty": self.repo.is_dirty(),
            "untracked_files": self.repo.untracked_files,
            "modified_files": [item.a_path for item in self.repo.index.diff(None)],
            "staged_files": staged_files
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
            logger.error(f"Error staging files: {e}", exc_info=True)
            return False
    
    def commit(self, message: str, author_name: Optional[str] = None, 
               author_email: Optional[str] = None) -> Optional[str]:
        """
        Commit staged changes and return commit SHA.
        
        Args:
            message: Commit message
            author_name: Optional author name (uses git config if not provided)
            author_email: Optional author email (uses git config if not provided)
            
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
            logger.error(f"Error committing: {e}", exc_info=True)
            return None
    
    def get_recent_commits(self, limit: int = 10) -> List[dict]:
        """
        Get recent commits from current branch.
        
        Args:
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries
        """
        commits = []
        for commit in self.repo.iter_commits(max_count=limit):
            commits.append({
                "sha": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": datetime.fromtimestamp(commit.committed_date)
            })
        return commits
    
    # ========================================================================
    # MERGE OPERATIONS
    # ========================================================================
    
    def merge_branch(self, branch_name: str, target_branch: str = "main") -> Tuple[bool, str]:
        """
        Merge a branch into target branch.
        
        Args:
            branch_name: Branch to merge
            target_branch: Target branch (default: main)
            
        Returns:
            Tuple of (success: bool, result: str)
            - If success: (True, merge_commit_sha)
            - If failure: (False, error_message)
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
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def generate_branch_name(self, category: str, action_type: str, title: str) -> str:
        """
        Generate a branch name from work item details.
        
        Args:
            category: Work item category (platform_feature, service, etc.)
            action_type: Action type (new, change, fix)
            title: Work item title
            
        Returns:
            Generated branch name (e.g., "service/new/endpoint-router-20251123")
        """
        # Sanitize title for branch name
        sanitized = title.lower().replace(" ", "-")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "-")
        sanitized = sanitized[:30]  # Limit length
        
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{category}/{action_type}/{sanitized}-{date_str}"
    
    def validate_for_commit(self) -> Tuple[bool, str]:
        """
        Validate repository is ready for commit.
        
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # Check if there are staged changes
        if not self.repo.index.diff("HEAD"):
            return False, "No staged changes to commit"
        
        return True, "Ready to commit"
    
    def check_changes_md_updated(self) -> bool:
        """
        Check if CHANGES.md was modified in current branch.
        
        Returns:
            True if CHANGES.md was modified, False otherwise
        """
        try:
            # Get diff between current branch and main
            diff = self.repo.git.diff('main', '--name-only')
            return 'docs/CHANGES.md' in diff
        except git.GitCommandError:
            return False

    @staticmethod
    def create_branch_in_repo(
        repo_path: str,
        branch_name: str,
        checkout: bool = True
    ) -> bool:
        """
        Create a Git branch in a specific repository.
        
        Args:
            repo_path: Path to Git repository (e.g., ~/calcifer/service-name)
            branch_name: Name of branch to create
            checkout: Whether to checkout the new branch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo_path_expanded = os.path.expanduser(repo_path)
            
            # Initialize repo if it doesn't exist
            if not os.path.exists(os.path.join(repo_path_expanded, '.git')):
                logger.info(f"Initializing Git repo at {repo_path_expanded}")
                repo = git.Repo.init(repo_path_expanded)
                
                # Create initial commit if repo is empty
                if not repo.heads:
                    # Create a README.md
                    readme_path = Path(repo_path_expanded) / "README.md"
                    readme_path.write_text(f"# Service Repository\n\nManaged by Calcifer.\n")
                    repo.index.add(['README.md'])
                    repo.index.commit("Initial commit")
                    logger.info("Created initial commit")
            else:
                repo = git.Repo(repo_path_expanded)
            
            # Create branch
            if branch_name in repo.heads:
                logger.warning(f"Branch {branch_name} already exists in {repo_path}")
                if checkout:
                    repo.heads[branch_name].checkout()
                return True
            
            new_branch = repo.create_head(branch_name)
            logger.info(f"Created branch '{branch_name}' in {repo_path}")
            
            if checkout:
                new_branch.checkout()
                logger.info(f"Checked out branch '{branch_name}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating branch in {repo_path}: {e}")
            return False
    
    @staticmethod
    def commit_to_repo(
        repo_path: str,
        message: str,
        files: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Commit changes to a specific repository.
        
        Args:
            repo_path: Path to Git repository
            message: Commit message
            files: List of files to stage (relative to repo root), or None for all changes
            
        Returns:
            Commit SHA if successful, None otherwise
        """
        try:
            repo_path_expanded = os.path.expanduser(repo_path)
            repo = git.Repo(repo_path_expanded)
            
            # Stage files
            if files:
                repo.index.add(files)
            else:
                repo.git.add(A=True)  # Add all changes
            
            # Check if there are changes to commit
            if not repo.index.diff("HEAD") and not repo.untracked_files:
                logger.info(f"No changes to commit in {repo_path}")
                return None
            
            # Commit
            commit = repo.index.commit(message)
            logger.info(f"Committed to {repo_path}: {commit.hexsha[:7]} - {message}")
            
            return commit.hexsha
            
        except Exception as e:
            logger.error(f"Error committing to {repo_path}: {e}")
            return None
    
    @staticmethod
    def get_repo_status(repo_path: str) -> Dict[str, Any]:
        """
        Get status of a specific repository.
        
        Args:
            repo_path: Path to Git repository
            
        Returns:
            Dictionary with repository status
        """
        try:
            repo_path_expanded = os.path.expanduser(repo_path)
            
            if not os.path.exists(os.path.join(repo_path_expanded, '.git')):
                return {
                    "initialized": False,
                    "current_branch": None,
                    "uncommitted_changes": False,
                    "untracked_files": []
                }
            
            repo = git.Repo(repo_path_expanded)
            
            return {
                "initialized": True,
                "current_branch": repo.active_branch.name if repo.heads else None,
                "uncommitted_changes": repo.is_dirty(),
                "untracked_files": repo.untracked_files,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff("HEAD")]
            }
            
        except Exception as e:
            logger.error(f"Error getting status for {repo_path}: {e}")
            return {
                "initialized": False,
                "error": str(e)
            }


# Singleton instance for easy import
git_module = GitModule(repo_path=repo_path)