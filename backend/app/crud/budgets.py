"""
Budgets CRUD operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .. import models, schemas

def get_budget_month(db: Session, user_id: int, budget_id: int, month: int) -> list[models.BudgetLine] | None:
    """Get budget lines for a specific month."""
    return db.query(models.BudgetLine).filter(
        models.BudgetLine.user_id == user_id,
        models.BudgetLine.budget_id == budget_id,
        models.BudgetLine.month == month
    ).all()

def get_budget(db: Session, user_id: int, budget_id: int) -> list[models.BudgetLine] | None:
    """Get all budget lines for a budget."""
    return db.query(models.BudgetLine).filter(
        models.BudgetLine.user_id == user_id,
        models.BudgetLine.budget_id == budget_id
    ).all()

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int = None) -> models.BudgetHeader:
    """Create a new budget with budget lines."""
    # Create budget header
    db_budget = models.BudgetHeader(
        user_id=user_id,
        name=budget.name,
        description=budget.description,
        start_month=budget.start_month,
        end_month=budget.end_month
    )
    db.add(db_budget)
    db.flush()  # Get the budget ID
    
    # Create budget lines
    for line_data in budget.lines:
        db_line = models.BudgetLine(
            budget_id=db_budget.id,
            user_id=user_id,
            account_id=line_data.account_id,
            month=line_data.month,
            amount=line_data.amount,
            currency=line_data.currency
        )
        db.add(db_line)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget: schemas.BudgetUpdate, user_id: int = None) -> models.BudgetHeader:
    """Update an existing budget."""
    db_budget = db.query(models.BudgetHeader).filter(
        models.BudgetHeader.id == budget_id,
        models.BudgetHeader.user_id == user_id
    ).first()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Update header fields
    for key, value in budget.model_dump(exclude_unset=True, exclude={'lines'}).items():
        setattr(db_budget, key, value)
    
    # Update budget lines if provided
    if budget.lines is not None:
        # Delete existing lines
        db.query(models.BudgetLine).filter(
            models.BudgetLine.budget_id == budget_id,
            models.BudgetLine.user_id == user_id
        ).delete()
        
        # Create new lines
        for line_data in budget.lines:
            db_line = models.BudgetLine(
                budget_id=budget_id,
                user_id=user_id,
                account_id=line_data.account_id,
                month=line_data.month,
                amount=line_data.amount,
                currency=line_data.currency
            )
            db.add(db_line)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int = None) -> None:
    """Delete a budget and all its lines."""
    # Delete budget lines first
    db.query(models.BudgetLine).filter(models.BudgetLine.budget_id == budget_id).delete()
    
    # Delete budget header
    db.query(models.BudgetHeader).filter(models.BudgetHeader.id == budget_id).delete()
    
    db.commit()
