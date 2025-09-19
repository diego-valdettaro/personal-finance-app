from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import budgets as crud_budgets
from ..database import get_db
from ..dependencies import get_authenticated_user
from ..models import User

router = APIRouter(prefix="/users/{user_id}/budgets", tags=["budgets"])

# Create a budget
@router.post("/", response_model=schemas.BudgetOut)
def create_budget(user_id: int, budget: schemas.BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    # Ensure budget.user_id matches the URL parameter
    if budget.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_budgets.create_budget(db, budget, user_id)

# Get monthly budget
@router.get("/{budget_id}/{month}", response_model=schemas.BudgetOut)
def get_budget_month(user_id: int, budget_id: int, month: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    budget = crud_budgets.get_budget_month(db, budget_id, month)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

# Get budget
@router.get("/{budget_id}", response_model=schemas.BudgetOut)
def get_budget(user_id: int, budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    budget = crud_budgets.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

# Update a budget
@router.patch("/{budget_id}", response_model=schemas.BudgetOut)
def update_budget(user_id: int, budget_id: int, budget: schemas.BudgetUpdate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_budgets.update_budget(db, budget_id, budget, user_id)

# Delete a yearly budget
@router.delete("/{budget_id}", status_code=204)
def delete_budget(user_id: int, budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_budgets.delete_budget(db, budget_id, user_id)
    return