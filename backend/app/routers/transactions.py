from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Create a transaction
@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, transaction.account_id)
    if not db_account:
        raise HTTPException(status_code=400, detail="Account not found")
    db_category = crud.get_category(db, transaction.category_id)
    if not db_category:
        raise HTTPException(status_code=400, detail="Category not found")
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
    db_transactions = crud.get_transactions(db, date_from, date_to, account_id, category_id, payer_person_id)
    if not db_transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return db_transactions

# Get a transaction
@router.get("/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

# Update a transaction
@router.patch("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.update_transaction(db, tx_id, transaction)

# Delete a transaction
@router.delete("/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db, tx_id)
    return

# Split a transaction
@router.post("/{tx_id}/split", response_model=schemas.TransactionOut)
def split_transaction(tx_id: int, payer_person_id: int, shares: list[schemas.TransactionShareCreate], db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction(db, tx_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.split_transaction(db, tx_id, payer_person_id, shares)