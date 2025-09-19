"""
Transaction splits CRUD operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from .. import models, schemas

def get_splits(db: Session, transaction_id: int) -> list[models.TxSplit]:
    """Get all splits for a transaction."""
    return db.query(models.TxSplit).filter(
        models.TxSplit.tx_id == transaction_id,
        models.TxSplit.active == True
    ).all()

def get_split(db: Session, split_id: int) -> models.TxSplit | None:
    """Get a single split by ID."""
    return db.query(models.TxSplit).filter(
        models.TxSplit.id == split_id,
        models.TxSplit.active == True
    ).first()

def set_splits_for_transaction(db: Session, transaction_id: int, splits: list[schemas.TxSplitCreate]) -> list[models.TxSplit]:
    """Set all splits for a transaction (replace existing splits)."""
    from .transactions import get_transaction

    # Get the transaction to validate amount
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Validate that splits sum to transaction amount
    total_split_amount = sum(split.share_amount for split in splits)
    transaction_amount = float(transaction.amount_oc_primary)

    if abs(total_split_amount - transaction_amount) > 0.01:  # Allow small floating point differences
        raise HTTPException(
            status_code=422,
            detail=f"Split total ({total_split_amount}) must equal transaction amount ({transaction_amount})"
        )

    # Clear existing splits for this transaction
    clear_splits_for_transaction(db, transaction_id)

    # Create new splits
    db_splits = []
    for split in splits:
        db_split = models.TxSplit(
            tx_id=transaction_id,
            person_id=split.person_id,
            share_amount=split.share_amount
        )
        db.add(db_split)
        db_splits.append(db_split)

    db.commit()
    
    # Refresh all splits to get their IDs
    for db_split in db_splits:
        db.refresh(db_split)
    
    return db_splits

def clear_splits_for_transaction(db: Session, transaction_id: int) -> None:
    """Clear all splits for a transaction."""
    # Hard delete all existing splits for this transaction
    db.query(models.TxSplit).filter(
        models.TxSplit.tx_id == transaction_id
    ).delete()
    
    db.commit()

# Individual split operations removed - splits are now managed as packages

def deactivate_splits_for_transaction(db: Session, transaction_id: int) -> None:
    """Deactivate all splits for a transaction (called when transaction is soft deleted)."""
    splits = db.query(models.TxSplit).filter(
        models.TxSplit.tx_id == transaction_id,
        models.TxSplit.active == True
    ).all()
    
    for split in splits:
        split.active = False
        split.deleted_at = func.now()
    
    db.commit()

def activate_splits_for_transaction(db: Session, transaction_id: int) -> None:
    """Activate all splits for a transaction (called when transaction is activated)."""
    splits = db.query(models.TxSplit).filter(
        models.TxSplit.tx_id == transaction_id,
        models.TxSplit.active == False
    ).all()
    
    for split in splits:
        split.active = True
        split.deleted_at = None
    
    db.commit()

def validate_splits_for_transaction(db: Session, transaction_id: int) -> schemas.TxSplitValidation:
    """Validate that splits sum to transaction amount."""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    splits = get_splits(db, transaction_id)
    total_split_amount = sum(float(split.share_amount) for split in splits)
    transaction_amount = float(transaction.amount_oc_primary)
    difference = abs(transaction_amount - total_split_amount)
    is_valid = difference < 0.01  # Allow for small floating point differences
    
    return schemas.TxSplitValidation(
        transaction_amount=transaction_amount,
        total_split_amount=total_split_amount,
        is_valid=is_valid,
        difference=difference
    )
