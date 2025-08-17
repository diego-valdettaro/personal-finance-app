from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Create an account
@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

# List all accounts
@router.get("/", response_model=list[schemas.AccountOut])
def get_accounts(db: Session = Depends(get_db)):
    return crud.get_accounts(db)

# Get an account
@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return crud.get_account(db, account_id)

# Update an account
@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db)):
    return crud.update_account(db, account_id, account)

# Delete an account
@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    crud.delete_account(db, account_id)
    return