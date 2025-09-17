from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Union
from .. import schemas
from ..crud import transactions as crud_transactions
from ..database import get_db
from ..dependencies import get_user_by_id
from ..models import User

router = APIRouter(prefix="/users/{user_id}/transactions", tags=["transactions"])

# Create a transaction
@router.post("/", response_model=schemas.TxOut)
def create_transaction(user_id: int, transaction: Union[schemas.TxCreate, schemas.TxCreateForex], db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_transactions.create_transaction(db, transaction)

# List all transactions for a user
@router.get("/", response_model=list[schemas.TxOut])
def get_transactions(
    user_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_user_by_id),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    account_id: Optional[int] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    payer_person_id: Optional[int] = Query(default=None),
):
    return crud_transactions.get_transactions(db, user_id=user_id, date_from=date_from, date_to=date_to, account_id=account_id, category_id=category_id, payer_person_id=payer_person_id)

# Get a transaction
@router.get("/{tx_id}", response_model=schemas.TxOut)
def get_transaction(user_id: int, tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_transactions.get_transaction(db, tx_id)

# Update a transaction
@router.patch("/{tx_id}", response_model=schemas.TxOut)
def update_transaction(user_id: int, tx_id: int, transaction: schemas.TxUpdate, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_transactions.update_transaction(db, tx_id, transaction)

# Deactivate a transaction (soft delete)
@router.delete("/{tx_id}", status_code=204)
def deactivate_transaction(user_id: int, tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    crud_transactions.deactivate_transaction(db, user_id=user_id, transaction_id=tx_id)
    return

# Activate a transaction (undo soft delete)
@router.post("/{tx_id}/activate", response_model=schemas.TxOut)
def activate_transaction(user_id: int, tx_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_transactions.activate_transaction(db, user_id=user_id, transaction_id=tx_id)