from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Create a transaction
@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

# List all transactions
@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    account_id: Optional[int] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    payer_person_id: Optional[int] = Query(default=None),
):
    return crud.get_transactions(db, date_from=date_from, date_to=date_to, account_id=account_id, category_id=category_id, payer_person_id=payer_person_id)

# Get a transaction
@router.get("/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    return crud.get_transaction(db, tx_id)

# Update a transaction
@router.patch("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    return crud.update_transaction(db, tx_id, transaction)

# Delete a transaction
@router.delete("/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    crud.delete_transaction(db, tx_id)
    return

# Split a transaction
@router.post("/{tx_id}/split", response_model=schemas.TransactionOut)
def split_transaction(tx_id: int, payer_person_id: int, shares: list[schemas.TransactionShareCreate], db: Session = Depends(get_db)):
    return crud.split_transaction(db, tx_id, payer_person_id, shares)