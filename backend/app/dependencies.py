"""
Dependencies for FastAPI endpoints.
"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .crud import users as crud_users
from .models import User
from .auth import get_current_user


def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> User:
    """Get a user by ID, raising 404 if not found."""
    user = crud_users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated user."""
    return current_user
