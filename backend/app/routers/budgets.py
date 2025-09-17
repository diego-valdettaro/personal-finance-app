from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import budgets as crud_budgets
from ..database import get_db

router = APIRouter(prefix="/budgets", tags=["budgets"])

# Create a budget
@router.post("/", response_model=schemas.BudgetOut)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    return crud_budgets.create_budget(db, budget)

# Get monthly budget
@router.get("/{id}/{month}", response_model=schemas.BudgetOut)
def get_budget(id: int, month: int, db: Session = Depends(get_db)):
    return crud_budgets.get_budget_month(db, id, month)

# Get budget
@router.get("/{id}", response_model=schemas.BudgetOut)
def get_budget(id: int, db: Session = Depends(get_db)):
    return crud_budgets.get_budget(db, id)

# Update a budget
@router.patch("/{id}", response_model=schemas.BudgetUpdate)
def update_budget(id: int, budget: schemas.BudgetUpdate, db: Session = Depends(get_db)):
    return crud_budgets.update_budget(db, id, budget)

# Delete a yearly budget
@router.delete("/{id}", status_code=204)
def delete_budget(id: int, db: Session = Depends(get_db)):
    crud_budgets.delete_budget(db, id)
    return