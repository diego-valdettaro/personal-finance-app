from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import reports as crud_reports
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

# Get balances
@router.get("/balances", response_model=list[schemas.ReportBalance])
def get_balances(db: Session = Depends(get_db)):
    return crud_reports.get_balances(db)

# Get debts
@router.get("/debts", response_model=list[schemas.ReportDebt])
def get_debts(db: Session = Depends(get_db)):
    return crud_reports.get_debts(db)

# Get budget progress
@router.get("/budget-progress/{month}", response_model=list[schemas.ReportBudgetProgress])
def get_budget_progress(month: str, db: Session = Depends(get_db)):
    return crud_reports.get_budget_progress(db, month)

# Get monthly budget progress for a specific budget
@router.get("/budget-progress/{budget_id}/{year}/{month}", response_model=schemas.ReportBudgetProgress)
def get_monthly_budget_progress(budget_id: int, year: int, month: int, db: Session = Depends(get_db)):
    return crud_reports.get_monthly_budget_progress(db, budget_id, year, month)