from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..crud import accounts as crud_accounts
from ..dependencies import get_authenticated_user
from ..models import User

router = APIRouter(prefix="/users/{user_id}/accounts", tags=["accounts"])

# Create an income/expense account
@router.post("/", response_model=schemas.AccountOut, status_code=201)
def create_income_expense_account(user_id: int, account: schemas.AccountCreateIncomeExpense, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    # Ensure account.user_id matches the URL parameter
    if account.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_accounts.create_account(db, account)

# Create an asset account
@router.post("/asset", response_model=schemas.AccountOut, status_code=201)
def create_asset_account(user_id: int, account: schemas.AccountCreateAsset, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    # Ensure account.user_id matches the URL parameter
    if account.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_accounts.create_account(db, account)

# Create a liability account
@router.post("/liability", response_model=schemas.AccountOut, status_code=201)
def create_liability_account(user_id: int, account: schemas.AccountCreateLiability, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    # Ensure account.user_id matches the URL parameter
    if account.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_accounts.create_account(db, account)

# List all accounts for a user
@router.get("/", response_model=list[schemas.AccountOut])
def get_accounts(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_accounts.get_accounts(db, user_id)

# Get an account
@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(user_id: int, account_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    account = crud_accounts.get_account(db, user_id, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Update an account
@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(user_id: int, account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_accounts.update_account(db, user_id, account_id, account)

# Deactivate an account
@router.patch("/{account_id}/deactivate", status_code=204)
def deactivate_account(user_id: int, account_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_accounts.deactivate_account(db, user_id, account_id)
    return None

# Activate an account
@router.patch("/{account_id}/activate", status_code=204)
def activate_account(user_id: int, account_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_accounts.activate_account(db, user_id, account_id)
    return None