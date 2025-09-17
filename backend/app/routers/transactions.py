from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Union
from .. import schemas
from ..crud import transactions as crud_transactions
from ..database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Create a transaction
@router.post("/", response_model=schemas.TxOut)
def create_transaction(transaction: Union[schemas.TxCreate, schemas.TxCreateForex], db: Session = Depends(get_db)):
    return crud_transactions.create_transaction(db, transaction)

# List all transactions
@router.get("/", response_model=list[schemas.TxOut])
def get_transactions(
    db: Session = Depends(get_db),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    account_id: Optional[int] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    payer_person_id: Optional[int] = Query(default=None),
):
    return crud_transactions.get_transactions(db, date_from=date_from, date_to=date_to, account_id=account_id, category_id=category_id, payer_person_id=payer_person_id)

# Get a transaction
@router.get("/{tx_id}", response_model=schemas.TxOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    return crud_transactions.get_transaction(db, tx_id)

# Update a transaction
@router.patch("/{tx_id}", response_model=schemas.TxOut)
def update_transaction(tx_id: int, transaction: schemas.TxUpdate, db: Session = Depends(get_db)):
    return crud_transactions.update_transaction(db, tx_id, transaction)

# Deactivate a transaction (soft delete)
@router.delete("/{tx_id}", status_code=204)
def deactivate_transaction(tx_id: int, db: Session = Depends(get_db)):
    crud_transactions.deactivate_transaction(db, user_id=1, transaction_id=tx_id)  # TODO: Get user_id from auth
    return

# Activate a transaction (undo soft delete)
@router.post("/{tx_id}/activate", response_model=schemas.TxOut)
def activate_transaction(tx_id: int, db: Session = Depends(get_db)):
    return crud_transactions.activate_transaction(db, user_id=1, transaction_id=tx_id)  # TODO: Get user_id from auth