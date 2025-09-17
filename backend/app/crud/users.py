"""
User CRUD operations.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .. import models, schemas
from .common import _validate_unique_user

def get_users(db: Session, user_ids: list[int] | None = None) -> list[models.User]:
    """Get all active users, optionally filtered by user IDs."""
    query = db.query(models.User).filter(models.User.active == True)
    if user_ids:
        query = query.filter(models.User.id.in_(user_ids))
    return query.all()

def get_user(db: Session, user_id: int) -> models.User | None:
    """Get a single active user by ID."""
    return db.query(models.User).filter(models.User.id == user_id, models.User.active == True).first()

def get_user_any_status(db: Session, user_id: int) -> models.User | None:
    """Get a user by ID regardless of active status."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    # Validate unique email
    _validate_unique_user(db=db, email=user.email)
    
    # Normalize currency to uppercase
    currency = user.home_currency.upper() if user.home_currency else None
    
    db_user = models.User(
        name=user.name,
        email=user.email,
        home_currency=currency
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    """Update an existing user."""
    db_user = get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate unique email if email is being updated
    if user.email is not None:
        _validate_unique_user(db=db, email=user.email, exclude_id=user_id)
    
    # Update fields
    for key, value in user.model_dump(exclude_unset=True).items():
        if key == "home_currency" and value is not None:
            value = value.upper()
        setattr(db_user, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int) -> None:
    """Deactivate a user (soft delete)."""
    db_user = get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if this is the last active user
    active_count = db.query(models.User).filter(models.User.active == True).count()
    if active_count <= 1:
        raise HTTPException(status_code=400, detail="Cannot deactivate last active user")
    
    db_user.active = False
    db_user.deleted_at = datetime.now()
    db.commit()

def activate_user(db: Session, user_id: int) -> None:
    """Activate a user."""
    db_user = get_user_any_status(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.active:
        raise HTTPException(status_code=404, detail="User is already active")
    
    db_user.active = True
    db_user.deleted_at = None
    db.commit()
