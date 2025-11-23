"""
Core Documentation Module

Handles documentation file management and rendering.
Documentation is stored as markdown files in docs/ directory.

This is CORE functionality - required for Calcifer to work.
"""

import os
import markdown
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class DocumentationModule:
    """
    Core module for documentation management.
    
    Handles:
    - Markdown file discovery
    - Documentation rendering
    - Change log management
    - Documentation file creation
    """
    
    def __init__(self, docs_path: str = "docs", repo_path: str = "."):
        """
        Initialize documentation module.
        
        Args:
            docs_path: Path to docs directory (relative to repo_path)
            repo_path: Path to repository root
        """
        self.repo_path = Path(repo_path)
        self.docs_path = self.repo_path / docs_path
        
        # Ensure docs directory exists
        self.docs_path.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # DOCUMENTATION DISCOVERY & RENDERING
    # ========================================================================
    
    def get_all_docs(self) -> List[Dict[str, str]]:
        """
        Get list of all markdown documentation files.
        
        Returns:
            List of dicts with name, title, and path
        """
        if not self.docs_path.exists():
            return []
        
        docs = []
        for file_path in self.docs_path.glob("*.md"):
            docs.append({
                "name": file_path.name,
                "title": file_path.stem.replace("_", " ").replace("-", " ").title(),
                "path": str(file_path.relative_to(self.repo_path))
            })
        
        # Sort by name
        docs.sort(key=lambda x: x["name"])
        
        return docs
    
    def get_doc_content(self, doc_name: str) -> Optional[str]:
        """
        Get raw markdown content of a documentation file.
        
        Args:
            doc_name: Name of the markdown file
            
        Returns:
            Raw markdown content or None if not found
        """
        doc_path = self.docs_path / doc_name
        
        if not doc_path.exists() or not doc_name.endswith(".md"):
            return None
        
        try:
            with open(doc_path, "r") as f:
                return f.read()
        except IOError:
            return None
    
    def render_doc_html(self, doc_name: str) -> Optional[str]:
        """
        Render documentation file as HTML.
        
        Args:
            doc_name: Name of the markdown file
            
        Returns:
            Rendered HTML or None if not found
        """
        content = self.get_doc_content(doc_name)
        
        if not content:
            return None
        
        # Convert markdown to HTML with extensions
        html = markdown.markdown(
            content,
            extensions=['fenced_code', 'tables', 'toc', 'codehilite']
        )
        
        return html
    
    # ========================================================================
    # CHANGES.MD MANAGEMENT
    # ========================================================================
    
    def ensure_changes_md_exists(self) -> bool:
        """
        Ensure CHANGES.md exists with header.
        
        Returns:
            True if successful
        """
        changes_path = self.docs_path / "CHANGES.md"
        
        if not changes_path.exists():
            with open(changes_path, "w") as f:
                f.write("# Change Log\n\n")
                f.write("All infrastructure changes are logged here.\n\n")
        
        return True
    
    def append_to_changes_md(
        self,
        entry: str,
        author: str,
        work_type: str
    ) -> bool:
        """
        Append an entry to CHANGES.md with proper formatting.
        
        Args:
            entry: Change description
            author: Author name
            work_type: Type of work (for the entry header)
            
        Returns:
            True if successful, False otherwise
        """
        self.ensure_changes_md_exists()
        changes_path = self.docs_path / "CHANGES.md"
        
        try:
            # Read current content
            with open(changes_path, 'r') as f:
                lines = f.readlines()
            
            # Format new entry
            today = datetime.now().strftime('%Y-%m-%d')
            new_entry = f"## {today} - {author} - {work_type}\n- {entry}\n"
            
            # Find insertion point (after header, before first ## entry)
            insert_index = len(lines)
            for i, line in enumerate(lines):
                if i > 0 and line.startswith('## '):
                    insert_index = i
                    break
            
            # Insert with proper spacing
            lines.insert(insert_index, '\n')
            lines.insert(insert_index + 1, new_entry)
            
            # Write updated CHANGES.md
            with open(changes_path, 'w') as f:
                f.writelines(lines)
            
            return True
        except IOError as e:
            print(f"Error writing to CHANGES.md: {e}")
            return False
    
    # ========================================================================
    # DOCUMENTATION CREATION
    # ========================================================================
    
    def create_doc(
        self,
        doc_name: str,
        content: str
    ) -> bool:
        """
        Create a new documentation file.
        
        Args:
            doc_name: Name of the file (should end in .md)
            content: Markdown content
            
        Returns:
            True if successful, False otherwise
        """
        if not doc_name.endswith('.md'):
            doc_name += '.md'
        
        doc_path = self.docs_path / doc_name
        
        try:
            with open(doc_path, 'w') as f:
                f.write(content)
            return True
        except IOError as e:
            print(f"Error creating documentation: {e}")
            return False
    
    def get_doc_path(self, doc_name: str) -> str:
        """
        Get the full path to a documentation file.
        
        Args:
            doc_name: Name of the file
            
        Returns:
            Full path to the file
        """
        if not doc_name.endswith('.md'):
            doc_name += '.md'
        
        return str(self.docs_path / doc_name)


# Singleton instance for easy import
documentation_module = DocumentationModule()