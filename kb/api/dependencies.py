# kb/api/dependencies.py

from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
import secrets

from ..core.database import get_session
from ..core.config import get_config


class APIKey:
    """Simple API key authentication"""

    def __init__(self):
        self.config = get_config()
        # In production, load from secure storage
        self.valid_keys = set(self.config.api_keys if hasattr(self.config, "api_keys") else [])

    def __call__(self, x_api_key: Optional[str] = Header(None)):
        # For local development, allow without API key
        if not self.valid_keys:
            return None

        if not x_api_key or x_api_key not in self.valid_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key"
            )

        return x_api_key


def get_current_user(api_key: str = Depends(APIKey())):
    """Get current user from API key (placeholder for future auth)"""
    # For now, return a default user
    # In production, implement proper user management
    return {"user_id": "default", "api_key": api_key}


def get_db_session() -> Session:
    """Dependency for database session"""
    return next(get_session())
