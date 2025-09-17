"""
Accounts CRUD operations.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import Union

from .. import models, schemas
from .common import _validate_unique_account, _validate_account_header, _validate_account_update

def get_accounts(db: Session, user_id: int, account_ids: list[int] | None = None) -> list[models.Account]:
    """Get all active accounts for a user, optionally filtered by account IDs."""
    query = db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.active == True
    )
    if account_ids:
        query = query.filter(models.Account.id.in_(account_ids))
    return query.all()

def get_account(db: Session, user_id: int, account_id: int) -> models.Account | None:
    """Get a single active account by ID for a specific user."""
    return db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.user_id == user_id,
        models.Account.active == True
    ).first()

def get_account_any_status(db: Session, user_id: int, account_id: int) -> models.Account | None:
    """Get an account by ID regardless of active status."""
    return db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.user_id == user_id
    ).first()

def create_account(db: Session, account: Union[schemas.AccountCreateIncomeExpense, schemas.AccountCreateAsset, schemas.AccountCreateLiability]) -> models.Account:
    """Create a new account."""
    # Validations
    _validate_unique_account(db=db, user_id=account.user_id, name=account.name, type=account.type)
    _validate_account_header(account=account)

    # Create account
    currency = getattr(account, "currency", None)
    if currency:
        currency = currency.upper()
    
    db_account = models.Account(
        user_id=account.user_id,
        name=account.name,
        type=account.type,
        currency=currency,    
        opening_balance=getattr(account, "opening_balance", None),
        current_balance=getattr(account, "opening_balance", None),
        bank_name=getattr(account, "bank_name", None),
        billing_day=getattr(account, "billing_day", None),
        due_day=getattr(account, "due_day", None)
    )
    db.add(db_account)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_account)
    return db_account

def update_account(db: Session, user_id: int, account_id: int, account: schemas.AccountUpdate) -> models.Account:
    """Update an existing account."""
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Validate unique name and type if being updated
    if account.name is not None or account.type is not None:
        name = account.name if account.name is not None else db_account.name
        type_val = account.type if account.type is not None else db_account.type
        _validate_unique_account(db=db, user_id=user_id, name=name, type=type_val, exclude_id=account_id)
    
    # Validate account update
    _validate_account_update(account=account, current_account=db_account)

    # Update fields
    for key, value in account.model_dump(exclude_unset=True).items():
        if key == "currency" and value is not None:
            value = value.upper()
        setattr(db_account, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_account)
    return db_account

def deactivate_account(db: Session, user_id: int, account_id: int) -> models.Account:
    """Deactivate an account (soft delete)."""
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db_account.active = False
    db_account.deleted_at = datetime.now()
    db.commit()
    return db_account

def activate_account(db: Session, user_id: int, account_id: int) -> models.Account:
    """Activate an account."""
    db_account = get_account_any_status(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if db_account.active:
        raise HTTPException(status_code=404, detail="Account is already active")
    
    db_account.active = True
    db_account.deleted_at = None
    db.commit()
    return db_account
