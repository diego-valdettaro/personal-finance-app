from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas
from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Create an income/expense account
@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_account(account: schemas.AccountCreateIncomeExpense, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

# Create an asset account
@router.post("/asset", response_model=schemas.AccountOut, status_code=201)
def create_asset_account(account: schemas.AccountCreateAsset, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

# Create a liability account
@router.post("/liability", response_model=schemas.AccountOut, status_code=201)
def create_liability_account(account: schemas.AccountCreateLiability, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

# List all accounts
@router.get("/", response_model=list[schemas.AccountOut])
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.get_accounts(db, current_user.id)

# Get an account
@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = crud.get_account(db, current_user.id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Update an account
@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.update_account(db, current_user.id, account_id, account)

# Deactivate an account
@router.patch("/{account_id}/deactivate", status_code=204)
def deactivate_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud.deactivate_account(db, current_user.id, account_id)
    return None

# Activate an account
@router.patch("/{account_id}/activate", status_code=204)
def activate_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud.activate_account(db, current_user.id, account_id)
    return None