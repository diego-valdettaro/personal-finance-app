"""
Transaction splits CRUD operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models

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
