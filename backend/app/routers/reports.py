from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

# Get balances
@router.get("/balances", response_model=list[schemas.ReportBalance])
def get_balances(db: Session = Depends(get_db)):
    return crud.get_balances(db)

# Get debts
@router.get("/debts", response_model=list[schemas.ReportDebt])
def get_debts(db: Session = Depends(get_db)):
    return crud.get_debts(db)

# Get budget progress
@router.get("/budget-progress/{month}", response_model=list[schemas.ReportBudgetProgress])
def get_budget_progress(month: str, db: Session = Depends(get_db)):
    return crud.get_budget_progress(db, month)