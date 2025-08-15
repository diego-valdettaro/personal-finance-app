from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

# Get balances
@router.get("/balances", response_model=List[schemas.ReportBalance])
def get_balances(db: Session = Depends(get_db)):
    return crud.get_balances(db)

# Get debts
@router.get("/debts", response_model=List[schemas.ReportDebt])
def get_debts(db: Session = Depends(get_db)):
    return crud.get_debts(db)