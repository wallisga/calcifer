"""Git integration for Calcifer - branch management and operations."""
import git
import os
from datetime import datetime
from typing import Optional, List, Tuple

class GitManager:
    """Manages Git operations for the infrastructure repository."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize Git manager with repository path."""
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            # If not a repo, initialize it
            self.repo = git.Repo.init(repo_path)
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        return self.repo.active_branch.name
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch and optionally check it out."""
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return True
        except git.GitCommandError as e:
            print(f"Error creating branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout an existing branch."""
        try:
            self.repo.git.checkout(branch_name)
            return True
        except git.GitCommandError as e:
            print(f"Error checking out branch: {e}")
            return False
    
    def get_branches(self) -> List[str]:
        """Get list of all branches."""
        return [head.name for head in self.repo.heads]
    
    def get_status(self) -> dict:
        """Get repository status."""
        return {
            "branch": self.get_current_branch(),
            "is_dirty": self.repo.is_dirty(),
            "untracked_files": self.repo.untracked_files,
            "modified_files": [item.a_path for item in self.repo.index.diff(None)],
            "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")]
        }
    
    def stage_files(self, files: List[str]) -> bool:
        """Stage files for commit."""
        try:
            self.repo.index.add(files)
            return True
        except git.GitCommandError as e:
            print(f"Error staging files: {e}")
            return False
    
    def commit(self, message: str, author_name: Optional[str] = None, 
               author_email: Optional[str] = None) -> Optional[str]:
        """Commit staged changes and return commit SHA."""
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
    
    def get_recent_commits(self, limit: int = 10) -> List[dict]:
        """Get recent commits."""
        commits = []
        for commit in self.repo.iter_commits(max_count=limit):
            commits.append({
                "sha": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": datetime.fromtimestamp(commit.committed_date)
            })
        return commits
    
    def generate_branch_name(self, work_type: str, title: str) -> str:
        """Generate a branch name from work item details."""
        # Sanitize title for branch name
        sanitized = title.lower().replace(" ", "-")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "-")
        sanitized = sanitized[:30]  # Limit length
        
        date_str = datetime.now().strftime("%Y%m%d")
        return f"{work_type}/{sanitized}-{date_str}"
    
    def ensure_changes_md_exists(self) -> bool:
        """Ensure docs/CHANGES.md exists."""
        changes_path = os.path.join(self.repo_path, "docs", "CHANGES.md")
        if not os.path.exists(changes_path):
            os.makedirs(os.path.dirname(changes_path), exist_ok=True)
            with open(changes_path, "w") as f:
                f.write("# Change Log\n\n")
                f.write("All infrastructure changes are logged here.\n\n")
        return True
    
    def append_to_changes_md(self, entry: str) -> bool:
        """Append an entry to CHANGES.md."""
        self.ensure_changes_md_exists()
        changes_path = os.path.join(self.repo_path, "docs", "CHANGES.md")
        
        try:
            with open(changes_path, "a") as f:
                f.write(f"\n{entry}\n")
            return True
        except IOError as e:
            print(f"Error writing to CHANGES.md: {e}")
            return False
    
    def validate_for_commit(self) -> Tuple[bool, str]:
        """Validate repository is ready for commit."""
        # Check if there are staged changes
        if not self.repo.index.diff("HEAD"):
            return False, "No staged changes to commit"
        
        # Check if CHANGES.md is staged
        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        if "docs/CHANGES.md" not in staged_files:
            return False, "docs/CHANGES.md must be updated and staged before committing"
        
        return True, "Ready to commit"