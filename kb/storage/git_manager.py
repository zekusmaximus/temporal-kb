# kb/storage/git_manager.py

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import git
from git import Repo, Actor
import logging

logger = logging.getLogger(__name__)

class GitManager:
    """
    Manages Git operations for knowledge base version control
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize Git manager
        
        Args:
            repo_path: Path to Git repository (usually data directory)
        """
        self.repo_path = repo_path
        self.repo: Optional[Repo] = None
        
        # Check if repo exists
        if (repo_path / ".git").exists():
            try:
                self.repo = Repo(repo_path)
                logger.debug(f"Opened existing Git repo at {repo_path}")
            except Exception as e:
                logger.error(f"Failed to open Git repo: {e}")
        else:
            logger.info(f"No Git repo found at {repo_path}")
    
    def init_repo(self) -> bool:
        """
        Initialize a new Git repository
        
        Returns:
            True if successful
        """
        try:
            self.repo = Repo.init(self.repo_path)
            
            # Create .gitignore
            gitignore_path = self.repo_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
*~

# Database (optional - you may want to version this)
# db/*.db
# db/*.db-shm
# db/*.db-wal

# Vector store (large binary files)
vectors/

# Logs
*.log
"""
                gitignore_path.write_text(gitignore_content)
                self.repo.index.add([str(gitignore_path)])
            
            # Initial commit
            self.commit("Initial commit: Knowledge base initialized")
            
            logger.info(f"Initialized Git repo at {self.repo_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize Git repo: {e}")
            return False
    
    def commit(
        self,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> bool:
        """
        Commit changes to Git
        
        Args:
            message: Commit message
            author_name: Author name (defaults to git config)
            author_email: Author email (defaults to git config)
            files: Specific files to commit (None = all changes)
        
        Returns:
            True if successful
        """
        if not self.repo:
            logger.warning("No Git repo available for commit")
            return False
        
        try:
            # Add files
            if files:
                self.repo.index.add(files)
            else:
                # Add all changes
                self.repo.git.add(A=True)
            
            # Check if there are changes to commit
            if not self.repo.index.diff("HEAD") and not self.repo.untracked_files:
                logger.debug("No changes to commit")
                return True
            
            # Create author if specified
            author = None
            if author_name and author_email:
                author = Actor(author_name, author_email)
            
            # Commit
            if author:
                self.repo.index.commit(message, author=author)
            else:
                self.repo.index.commit(message)
            
            logger.debug(f"Committed: {message}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to commit: {e}")
            return False
    
    def get_history(
        self,
        max_count: int = 50,
        file_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get commit history
        
        Args:
            max_count: Maximum number of commits to retrieve
            file_path: Specific file path to filter commits
        
        Returns:
            List of commit information
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            
            if file_path:
                # Get commits for specific file
                commit_iter = self.repo.iter_commits(paths=file_path, max_count=max_count)
            else:
                # Get all commits
                commit_iter = self.repo.iter_commits(max_count=max_count)
            
            for commit in commit_iter:
                commits.append({
                    'sha': commit.hexsha,
                    'short_sha': commit.hexsha[:7],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date),
                    'files_changed': len(commit.stats.files)
                })
            
            return commits
        
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    def get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get commit history for a specific file"""
        return self.get_history(file_path=file_path)
    
    def get_diff(
        self,
        commit_sha: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> str:
        """
        Get diff for a commit or current changes
        
        Args:
            commit_sha: Commit SHA (None = working directory changes)
            file_path: Specific file to show diff for
        
        Returns:
            Diff as string
        """
        if not self.repo:
            return ""
        
        try:
            if commit_sha:
                commit = self.repo.commit(commit_sha)
                if file_path:
                    return commit.diff(commit.parents[0], paths=file_path, create_patch=True)
                else:
                    return commit.diff(commit.parents[0], create_patch=True)
            else:
                # Show working directory changes
                if file_path:
                    return self.repo.git.diff(file_path)
                else:
                    return self.repo.git.diff()
        
        except Exception as e:
            logger.error(f"Failed to get diff: {e}")
            return ""
    
    def checkout_file(self, file_path: str, commit_sha: str) -> bool:
        """
        Restore a file from a specific commit
        
        Args:
            file_path: Path to file
            commit_sha: Commit to restore from
        
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            self.repo.git.checkout(commit_sha, file_path)
            logger.info(f"Restored {file_path} from {commit_sha[:7]}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to checkout file: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        if not self.repo:
            return False
        
        try:
            self.repo.create_head(branch_name)
            logger.info(f"Created branch: {branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a different branch"""
        if not self.repo:
            return False
        
        try:
            self.repo.heads[branch_name].checkout()
            logger.info(f"Switched to branch: {branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to switch branch: {e}")
            return False
    
    def push(self, remote_name: str = "origin", branch_name: str = "main") -> bool:
        """
        Push commits to remote repository
        
        Args:
            remote_name: Name of remote
            branch_name: Branch to push
        
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            remote = self.repo.remote(name=remote_name)
            remote.push(branch_name)
            logger.info(f"Pushed to {remote_name}/{branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to push: {e}")
            return False
    
    def pull(self, remote_name: str = "origin", branch_name: str = "main") -> bool:
        """
        Pull changes from remote repository
        
        Args:
            remote_name: Name of remote
            branch_name: Branch to pull
        
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            remote = self.repo.remote(name=remote_name)
            remote.pull(branch_name)
            logger.info(f"Pulled from {remote_name}/{branch_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to pull: {e}")
            return False
    
    def add_remote(self, name: str, url: str) -> bool:
        """
        Add a remote repository
        
        Args:
            name: Remote name
            url: Remote URL
        
        Returns:
            True if successful
        """
        if not self.repo:
            return False
        
        try:
            self.repo.create_remote(name, url)
            logger.info(f"Added remote: {name} -> {url}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add remote: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get repository status
        
        Returns:
            Dict with status information
        """
        if not self.repo:
            return {"initialized": False}
        
        try:
            return {
                "initialized": True,
                "branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                "commit_count": len(list(self.repo.iter_commits())),
                "latest_commit": {
                    "sha": self.repo.head.commit.hexsha[:7],
                    "message": self.repo.head.commit.message.strip(),
                    "date": datetime.fromtimestamp(self.repo.head.commit.committed_date)
                }
            }
        
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"initialized": True, "error": str(e)}