"""
Reports CRUD operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .. import models, schemas

def get_balances(db: Session, user_id: int) -> list[schemas.ReportBalance]:
    """Get account balances report."""
    balances = db.query(
        models.Account.id,
        models.Account.name,
        models.Account.type,
        models.Account.currency,
        models.Account.current_balance
    ).filter(
        models.Account.active == True,
        models.Account.user_id == user_id
    ).all()
    
    return [
        schemas.ReportBalance(
            account_id=balance.id,
            account_name=balance.name,
            account_type=balance.type,
            currency=balance.currency or "EUR",  # Default to EUR if currency is None
            balance=balance.current_balance or 0.0
        )
        for balance in balances
    ]

def get_debts(db: Session, user_id: int) -> list[schemas.ReportDebt]:
    """Get debts report based on transaction splits."""
    from sqlalchemy import func
    from collections import defaultdict
    
    # Get all people for this user
    people = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.active == True
    ).all()
    
    # Calculate debts for each person based on splits
    debts = []
    for person in people:
        # Get all splits for this person
        splits = db.query(models.TxSplit).join(models.Transaction).filter(
            models.TxSplit.person_id == person.id,
            models.TxSplit.active == True,
            models.Transaction.user_id == user_id,
            models.Transaction.active == True
        ).all()
        
        # Calculate total debt (sum of all splits)
        total_debt = sum(float(split.share_amount) for split in splits)
        
        debts.append(schemas.ReportDebt(
            person_id=person.id,
            person_name=person.name,
            debt=total_debt,
            is_active=total_debt > 0
        ))
    
    return debts

def get_budget_progress(db: Session, user_id: int, month: str) -> list[schemas.ReportBudgetProgress]:
    """Get budget progress for a month (simplified implementation)."""
    # This is a simplified implementation
    # In a real application, this would calculate actual vs budgeted amounts
    return []

def get_monthly_budget_progress(db: Session, user_id: int, budget_id: int, year: int, month: int) -> list[schemas.ReportBudgetProgress]:
    """Get monthly budget progress report."""
    # Check if budget exists and belongs to user
    budget = db.query(models.BudgetHeader).filter(
        models.BudgetHeader.id == budget_id,
        models.BudgetHeader.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # This is a simplified implementation
    # In a real application, this would calculate actual vs budgeted amounts
    budget_lines = db.query(models.BudgetLine).join(models.Account).filter(
        models.BudgetLine.header_id == budget_id,
        models.BudgetLine.month == month
    ).all()
    
    return [
            schemas.ReportBudgetProgress(
                account_id=line.account_id,
                account_name=line.account.name,
                budget_hc=float(line.amount_hc),
                actual_hc=0.0,  # Would be calculated from actual transactions
                progress=0.0  # Would be calculated as actual_hc / budget_hc
            )
            for line in budget_lines
        ]
