"""
Common utilities and validation functions for CRUD operations.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Union

from .. import models, schemas

#--------------------------------
# Constants
#--------------------------------
BALANCE_ABS_TOL = 0.000001

#--------------------------------
# Validation functions
#--------------------------------
def _validate_unique_user(db: Session, email: str | None, exclude_id: int | None = None) -> None:
    query = db.query(models.User)
    q = query.filter(models.User.email == email)
    if exclude_id is not None:
        q = q.filter(models.User.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"User with email {email} already exists")

def _validate_unique_person(db: Session, user_id: int, name: str, is_me: bool, exclude_id: int | None = None) -> None:
    query = db.query(models.Person)
    q = query.filter(
        models.Person.user_id == user_id,
        models.Person.name == name
    )
    if exclude_id is not None:
        q = q.filter(models.Person.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"Person with name {name} already exists for user {user_id}")
    if is_me:
        q_me = db.query(models.Person).filter(
            models.Person.user_id == user_id,
            models.Person.is_me == True
        )
        if exclude_id is not None:
            q_me = q_me.filter(models.Person.id != exclude_id)
        if q_me.first():
            raise HTTPException(status_code=409, detail=f"User {user_id} already has a me person defined")

def _validate_unique_account(db: Session, user_id: int, name: str, type: models.AccountType, exclude_id: int | None = None) -> None:
    query = db.query(models.Account)    
    q = query.filter(
        models.Account.user_id == user_id,
        models.Account.name == name,
        models.Account.type == type
    )
    if exclude_id is not None:
        q = q.filter(models.Account.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"Account with name {name} and type {type} already exists for user {user_id}")

def _validate_account_header(account: Union[schemas.AccountCreateIncomeExpense, schemas.AccountCreateAsset, schemas.AccountCreateLiability]) -> None:
    if account.type in [models.AccountType.asset, models.AccountType.liability]:
        if not hasattr(account, 'currency') or account.currency is None:
            raise HTTPException(status_code=400, detail="Currency is required for asset and liability accounts")
        if account.type == models.AccountType.asset:
            if hasattr(account, 'billing_day') and account.billing_day is not None:
                raise HTTPException(status_code=400, detail="Billing day should not be specified for asset accounts")
            if hasattr(account, 'due_day') and account.due_day is not None:
                raise HTTPException(status_code=400, detail="Due day should not be specified for asset accounts")
    else:
        if hasattr(account, 'currency') and account.currency is not None:
            raise HTTPException(status_code=400, detail="Currency should not be specified for income and expense accounts")
        if hasattr(account, 'bank_name') and account.bank_name is not None:
            raise HTTPException(status_code=400, detail="Bank name should not be specified for income and expense accounts")
        if hasattr(account, 'opening_balance') and account.opening_balance is not None:
            raise HTTPException(status_code=400, detail="Opening balance should not be specified for income and expense accounts")
        if hasattr(account, 'billing_day') and account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for income and expense accounts")
        if hasattr(account, 'due_day') and account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for income and expense accounts")

def _validate_account_update(account: schemas.AccountUpdate, current_account: models.Account) -> None:
    """Validate account update data against current account state."""
    # If type is being changed, validate the new type requirements
    if account.type is not None:
        if account.type in [models.AccountType.asset, models.AccountType.liability]:
            # For asset/liability accounts, currency is required
            if account.currency is None and current_account.currency is None:
                raise HTTPException(status_code=400, detail="Currency is required for asset and liability accounts")
        else:
            # For income/expense accounts, currency should not be specified
            if account.currency is not None:
                raise HTTPException(status_code=400, detail="Currency should not be specified for income and expense accounts")
    
    # Validate fields based on final account type
    final_type = account.type if account.type is not None else current_account.type
    if final_type == models.AccountType.asset:
        if account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for asset accounts")
        if account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for asset accounts")
    elif final_type in [models.AccountType.income, models.AccountType.expense]:
        if account.currency is not None:
            raise HTTPException(status_code=400, detail="Currency should not be specified for income and expense accounts")
        if account.bank_name is not None:
            raise HTTPException(status_code=400, detail="Bank name should not be specified for income and expense accounts")
        if account.opening_balance is not None:
            raise HTTPException(status_code=400, detail="Opening balance should not be specified for income and expense accounts")
        if account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for income and expense accounts")
        if account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for income and expense accounts")

def _validate_tx_header(tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> None:
    """Validate transaction header data."""
    if tx.type == models.TxType.forex:
        if not hasattr(tx, 'currency_primary') or not hasattr(tx, 'currency_secondary'):
            raise HTTPException(status_code=400, detail="Forex transactions require currency_primary and currency_secondary")
        if tx.currency_primary == tx.currency_secondary:
            raise HTTPException(status_code=400, detail="Forex transactions cannot have the same primary and secondary currency")
    else:
        if hasattr(tx, 'currency_secondary'):
            raise HTTPException(status_code=400, detail="Non-forex transactions should not specify currency_secondary")

def _build_postings_from_tx_input(tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> list[schemas.TxPostingCreateAutomatic]:
    """Build postings from transaction input data."""
    postings = []
    
    if tx.type == models.TxType.forex:
        # Forex transaction: primary_currency -> secondary_currency
        postings.append(schemas.TxPostingCreateAutomatic(
            account_id=tx.account_id_primary,
            amount_oc=-tx.amount_oc_primary,
            currency=tx.currency_primary
        ))
        postings.append(schemas.TxPostingCreateAutomatic(
            account_id=tx.account_id_secondary,
            amount_oc=tx.amount_oc_secondary,
            currency=tx.currency_secondary
        ))
    else:
        # Regular transaction: determine signs based on transaction type
        if tx.type == models.TxType.income:
            # Income: credit income account, debit asset account
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_primary,  # Income account
                amount_oc=tx.amount_oc_primary,   # Positive (credit)
                currency=tx.currency_primary
            ))
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_secondary,  # Asset account
                amount_oc=-tx.amount_oc_primary,    # Negative (debit)
                currency=tx.currency_primary
            ))
        elif tx.type == models.TxType.expense:
            # Expense: debit expense account, credit asset account
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_primary,  # Expense account
                amount_oc=tx.amount_oc_primary,   # Positive (debit)
                currency=tx.currency_primary
            ))
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_secondary,  # Asset account
                amount_oc=-tx.amount_oc_primary,    # Negative (credit)
                currency=tx.currency_primary
            ))
        elif tx.type == models.TxType.transfer:
            # Transfer: debit source account, credit destination account
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_primary,  # Source account
                amount_oc=-tx.amount_oc_primary,   # Negative (debit)
                currency=tx.currency_primary
            ))
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_secondary,  # Destination account
                amount_oc=tx.amount_oc_primary,     # Positive (credit)
                currency=tx.currency_primary
            ))
        elif tx.type == models.TxType.credit_card_payment:
            # Credit card payment: debit credit card account, credit asset account
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_primary,  # Credit card account
                amount_oc=-tx.amount_oc_primary,   # Negative (debit)
                currency=tx.currency_primary
            ))
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_secondary,  # Asset account
                amount_oc=tx.amount_oc_primary,     # Positive (credit)
                currency=tx.currency_primary
            ))
        else:
            # Default: primary_account -> secondary_account (both positive)
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_primary,
                amount_oc=tx.amount_oc_primary,
                currency=tx.currency_primary
            ))
            postings.append(schemas.TxPostingCreateAutomatic(
                account_id=tx.account_id_secondary,
                amount_oc=tx.amount_oc_primary,
                currency=tx.currency_primary
            ))
    
    return postings

def _validate_and_complete_postings(db: Session, transaction: models.Transaction, postings: list[schemas.TxPostingCreateAutomatic]) -> list[models.TxPosting]:
    """Validate and complete posting data."""
    completed_postings = []
    
    for posting_data in postings:
        # Get account details
        account = db.query(models.Account).filter(models.Account.id == posting_data.account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {posting_data.account_id} not found")
        
        # Validate currency matches account currency (if account has currency)
        if account.currency and posting_data.currency != account.currency:
            raise HTTPException(status_code=400, detail=f"Posting currency {posting_data.currency} does not match account currency {account.currency}")
        
        # Create posting
        posting = models.TxPosting(
            tx_id=transaction.id,
            account_id=posting_data.account_id,
            amount_oc=posting_data.amount_oc,
            currency=posting_data.currency,
            amount_hc=posting_data.amount_oc  # For now, assume same as amount_oc
        )
        db.add(posting)
        completed_postings.append(posting)
    
    return completed_postings

