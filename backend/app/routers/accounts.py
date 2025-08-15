from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Create an account
@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account.name)
    if db_account:
        raise HTTPException(status_code=400, detail="Account name already exists")
    return crud.create_account(db, account)

# List all accounts
@router.get("/", response_model=List[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    db_accounts = crud.get_accounts(db)
    if not db_accounts:
        raise HTTPException(status_code=404, detail="No accounts found")
    return db_accounts

# Get an account
@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

# Update an account
@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return crud.update_account(db, account_id, account)

# Delete an account
@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    crud.delete_account(db, account_id)
    return