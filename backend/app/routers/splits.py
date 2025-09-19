"""
Transaction splits router - Splitwise-like package management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models
from ..dependencies import get_authenticated_user
from ..crud import splits as crud_splits, transactions as crud_transactions

router = APIRouter(prefix="/users/{user_id}/transactions/{transaction_id}/splits", tags=["splits"])

@router.get("/", response_model=list[schemas.TxSplitOut])
def get_splits(
    user_id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_authenticated_user)
):
    """Get all splits for a transaction."""
    # Verify transaction belongs to user
    transaction = crud_transactions.get_transaction(db, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return crud_splits.get_splits(db, transaction_id)

@router.put("/", response_model=list[schemas.TxSplitOut])
def set_splits(
    user_id: int,
    transaction_id: int,
    splits: list[schemas.TxSplitCreate],
    db: Session = Depends(get_db),
    user: models.User = Depends(get_authenticated_user)
):
    """Set all splits for a transaction (replace existing splits)."""
    # Verify transaction belongs to user
    transaction = crud_transactions.get_transaction(db, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return crud_splits.set_splits_for_transaction(db, transaction_id, splits)

@router.delete("/")
def clear_splits(
    user_id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_authenticated_user)
):
    """Clear all splits for a transaction."""
    # Verify transaction belongs to user
    transaction = crud_transactions.get_transaction(db, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    crud_splits.clear_splits_for_transaction(db, transaction_id)
    return {"message": "All splits cleared successfully"}

@router.get("/validation", response_model=schemas.TxSplitValidation)
def validate_splits(
    user_id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_authenticated_user)
):
    """Validate that splits sum to transaction amount."""
    # Verify transaction belongs to user
    transaction = crud_transactions.get_transaction(db, transaction_id)
    if not transaction or transaction.user_id != user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return crud_splits.validate_splits_for_transaction(db, transaction_id)
