"""
Reports CRUD operations.
"""
from sqlalchemy.orm import Session

from .. import models, schemas

def get_balances(db: Session) -> list[schemas.ReportBalance]:
    """Get account balances report."""
    balances = db.query(
        models.Account.id,
        models.Account.name,
        models.Account.type,
        models.Account.currency,
        models.Account.current_balance
    ).filter(
        models.Account.active == True
    ).all()
    
    return [
        schemas.ReportBalance(
            account_id=balance.id,
            account_name=balance.name,
            account_type=balance.type,
            currency=balance.currency,
            balance=balance.current_balance or 0.0
        )
        for balance in balances
    ]

def get_debts(db: Session) -> list[schemas.ReportDebt]:
    """Get debts report (liability accounts)."""
    debts = db.query(
        models.Account.id,
        models.Account.name,
        models.Account.currency,
        models.Account.current_balance,
        models.Account.billing_day,
        models.Account.due_day
    ).filter(
        models.Account.active == True,
        models.Account.type == models.AccountType.liability
    ).all()
    
    return [
        schemas.ReportDebt(
            account_id=debt.id,
            account_name=debt.name,
            currency=debt.currency,
            balance=debt.current_balance or 0.0,
            billing_day=debt.billing_day,
            due_day=debt.due_day
        )
        for debt in debts
    ]

def get_budget_progress(db: Session, month: str, user_id: int = None) -> list[schemas.ReportBudgetProgress]:
    """Get budget progress for a month (simplified implementation)."""
    # This is a simplified implementation
    # In a real application, this would calculate actual vs budgeted amounts
    return []

def get_monthly_budget_progress(db: Session, budget_id: int, year: int, month: int, user_id: int = None) -> list[schemas.ReportBudgetProgress]:
    """Get monthly budget progress report."""
    # This is a simplified implementation
    # In a real application, this would calculate actual vs budgeted amounts
    budget_lines = db.query(models.BudgetLine).filter(
        models.BudgetLine.user_id == user_id,
        models.BudgetLine.budget_id == budget_id,
        models.BudgetLine.month == month
    ).all()
    
    return [
        schemas.ReportBudgetProgress(
            account_id=line.account_id,
            budgeted_amount=line.amount,
            actual_amount=0.0,  # Would be calculated from actual transactions
            currency=line.currency,
            variance=0.0 - line.amount
        )
        for line in budget_lines
    ]
