from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import reports as crud_reports
from ..database import get_db
from ..dependencies import get_user_by_id
from ..models import User

router = APIRouter(prefix="/users/{user_id}/reports", tags=["reports"])

# Get balances
@router.get("/balances", response_model=list[schemas.ReportBalance])
def get_balances(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_reports.get_balances(db, user_id)

# Get debts
@router.get("/debts", response_model=list[schemas.ReportDebt])
def get_debts(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_reports.get_debts(db, user_id)

# Get budget progress
@router.get("/budget-progress/{month}", response_model=list[schemas.ReportBudgetProgress])
def get_budget_progress(user_id: int, month: str, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_reports.get_budget_progress(db, user_id, month)

# Get monthly budget progress for a specific budget
@router.get("/budget-progress/{budget_id}/{year}/{month}", response_model=schemas.ReportBudgetProgress)
def get_monthly_budget_progress(user_id: int, budget_id: int, year: int, month: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_reports.get_monthly_budget_progress(db, user_id, budget_id, year, month)