"""
Transaction postings CRUD operations.
"""
from sqlalchemy.orm import Session

from .. import models

def get_postings(db: Session, transaction_id: int) -> list[models.TxPosting]:
    """Get all active postings for a transaction."""
    return db.query(models.TxPosting).filter(
        models.TxPosting.tx_id == transaction_id,
        models.TxPosting.active == True
    ).all()

def get_posting(db: Session, posting_id: int) -> models.TxPosting | None:
    """Get a single active posting by ID."""
    return db.query(models.TxPosting).filter(
        models.TxPosting.id == posting_id,
        models.TxPosting.active == True
    ).first()
