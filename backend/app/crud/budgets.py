"""
Budgets CRUD operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .. import models, schemas

def get_budget_month(db: Session, budget_id: int, month: int) -> models.BudgetHeader | None:
    """Get budget header with lines for a specific month."""
    from sqlalchemy.orm import joinedload
    budget = db.query(models.BudgetHeader).options(
        joinedload(models.BudgetHeader.budget_lines)
    ).filter(models.BudgetHeader.id == budget_id).first()
    
    if budget:
        # Filter the budget lines to only include the specified month
        budget.budget_lines = [line for line in budget.budget_lines if line.month == month]
    
    return budget

def get_budget(db: Session, budget_id: int) -> models.BudgetHeader | None:
    """Get a budget header with its lines."""
    from sqlalchemy.orm import joinedload
    return db.query(models.BudgetHeader).options(
        joinedload(models.BudgetHeader.budget_lines)
    ).filter(models.BudgetHeader.id == budget_id).first()

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int = None) -> models.BudgetHeader:
    """Create a new budget with budget lines."""
    # Create budget header
    db_budget = models.BudgetHeader(
        user_id=user_id,
        name=budget.name,
        year=budget.year
    )
    db.add(db_budget)
    
    try:
        db.flush()  # Get the budget ID
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Budget with this name and year already exists for this user")
    
    # Create budget lines
    for line_data in budget.lines:
        db_line = models.BudgetLine(
            header_id=db_budget.id,
            account_id=line_data.account_id,
            month=line_data.month,
            amount_oc=line_data.amount_oc,
            currency=line_data.currency,
            amount_hc=line_data.amount_hc,
            fx_rate=line_data.fx_rate,
            description=line_data.description
        )
        db.add(db_line)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_budget)
    
    # Explicitly load the budget lines to ensure they're included in the response
    from sqlalchemy.orm import joinedload
    db_budget = db.query(models.BudgetHeader).options(joinedload(models.BudgetHeader.budget_lines)).filter(models.BudgetHeader.id == db_budget.id).first()
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
            models.BudgetLine.header_id == budget_id
        ).delete()
        
        # Create new lines
        for line_data in budget.lines:
            db_line = models.BudgetLine(
                header_id=budget_id,
                account_id=line_data.account_id,
                month=line_data.month,
                amount_oc=line_data.amount_oc,
                currency=line_data.currency,
                amount_hc=line_data.amount_hc,
                fx_rate=line_data.fx_rate,
                description=line_data.description
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
    # Check if budget exists
    budget = db.query(models.BudgetHeader).filter(
        models.BudgetHeader.id == budget_id,
        models.BudgetHeader.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Delete budget lines first
    db.query(models.BudgetLine).filter(models.BudgetLine.header_id == budget_id).delete()
    
    # Delete budget header
    db.query(models.BudgetHeader).filter(models.BudgetHeader.id == budget_id).delete()
    
    db.commit()
