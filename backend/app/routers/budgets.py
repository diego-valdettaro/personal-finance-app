from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import budgets as crud_budgets
from ..database import get_db
from ..dependencies import get_user_by_id
from ..models import User

router = APIRouter(prefix="/users/{user_id}/budgets", tags=["budgets"])

# Create a budget
@router.post("/", response_model=schemas.BudgetOut)
def create_budget(user_id: int, budget: schemas.BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    # Ensure budget.user_id matches the URL parameter
    if budget.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_budgets.create_budget(db, budget)

# Get monthly budget
@router.get("/{budget_id}/{month}", response_model=schemas.BudgetOut)
def get_budget_month(user_id: int, budget_id: int, month: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_budgets.get_budget_month(db, budget_id, month)

# Get budget
@router.get("/{budget_id}", response_model=schemas.BudgetOut)
def get_budget(user_id: int, budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_budgets.get_budget(db, budget_id)

# Update a budget
@router.patch("/{budget_id}", response_model=schemas.BudgetUpdate)
def update_budget(user_id: int, budget_id: int, budget: schemas.BudgetUpdate, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    return crud_budgets.update_budget(db, budget_id, budget)

# Delete a yearly budget
@router.delete("/{budget_id}", status_code=204)
def delete_budget(user_id: int, budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_user_by_id)):
    crud_budgets.delete_budget(db, budget_id)
    return