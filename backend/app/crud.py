from datetime import datetime, date

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from math import isfinite, isclose
from typing import Union, Dict

from . import models, schemas

#--------------------------------
# Constants
#--------------------------------
BALANCE_ABS_TOL = 0.000001

#--------------------------------
# Helper functions
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
            raise HTTPException(status_code=400, detail="Currency should not be specified for non-asset and non-liability accounts")
        if hasattr(account, 'bank_name') and account.bank_name is not None:
            raise HTTPException(status_code=400, detail="Bank name should not be specified for non-asset and non-liability accounts")
        if hasattr(account, 'opening_balance') and account.opening_balance is not None:
            raise HTTPException(status_code=400, detail="Opening balance should not be specified for non-asset and non-liability accounts")
        if hasattr(account, 'billing_day') and account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for non-asset and non-liability accounts")
        if hasattr(account, 'due_day') and account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for non-asset and non-liability accounts")

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
    
    # Validate billing_day and due_day based on account type
    final_type = account.type if account.type is not None else current_account.type
    if final_type == models.AccountType.asset:
        if account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for asset accounts")
        if account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for asset accounts")
    elif final_type in [models.AccountType.income, models.AccountType.expense]:
        if account.billing_day is not None:
            raise HTTPException(status_code=400, detail="Billing day should not be specified for income and expense accounts")
        if account.due_day is not None:
            raise HTTPException(status_code=400, detail="Due day should not be specified for income and expense accounts")

def _validate_tx_header(tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> None:
    """
    Validate the header of a transaction without DB access.
    """
    # ---- helpers (local, tiny) ----
    def _is_forex_type(t) -> bool:
        return str(t).lower().endswith("forex")  # works for enums and strings

    def _valid_ccy(ccy: str) -> bool:
        return isinstance(ccy, str) and len(ccy) == 3 and ccy.isalpha()

    def _pos_number(x) -> bool:
        return x is not None and isinstance(x, (int, float)) and isfinite(x) and x > 0

    # Validate that accounts are different
    if tx.account_id_primary == tx.account_id_secondary:
        raise HTTPException(status_code=400, detail="Origin and destination accounts cannot be the same")

    # Validate that the amount and currency are provided for the primary account
    if not _pos_number(tx.amount_oc_primary):
        raise HTTPException(status_code=400, detail="Primary amount must be a positive number")
    if not _valid_ccy(tx.currency_primary):
        raise HTTPException(status_code=400, detail="Primary currency must be a 3-letter ISO code (e.g. USD, EUR).")

    # Validate type and schema coherence
    is_forex_declared = _is_forex_type(tx.type)
    is_forex_payload = hasattr(tx, "amount_oc_secondary") and hasattr(tx, "currency_secondary")
    # Validate TxCreateForex schema has type == forex
    if isinstance(tx, schemas.TxCreateForex) and not is_forex_declared:
        raise HTTPException(status_code=400, detail="TxCreateForex schema must declare as type 'forex'")

    # Validate TxCreate schema has type != forex
    if isinstance(tx, schemas.TxCreate) and is_forex_declared:
        raise HTTPException(status_code=400, detail="TxCreate schema cannot declare as type 'forex'")

    # Forex transaction validations
    if is_forex_declared:
        # Must provide secondary leg explicitly
        if not is_forex_payload:
            raise HTTPException(status_code=400, detail="TxCreateForex schema must provide amount_oc_secondary and currency_secondary")
        
        # Validate secondary amount/currency
        if not _pos_number(tx.amount_oc_secondary):
            raise HTTPException(status_code=400, detail="Secondary amount must be a positive number")
        if not _valid_ccy(tx.currency_secondary):
            raise HTTPException(status_code=400, detail="Secondary currency must be a 3-letter ISO code (e.g. USD, EUR).")
        
        # Cureencies must be different in a forex transaction
        if tx.currency_primary.upper() == tx.currency_secondary.upper():
            raise HTTPException(status_code=400, detail="Forex transactions require two accounts with different currencies")
    # Non-forex transaction validations
    else:
        # Secondary leg must not be provided
        if is_forex_payload:
            raise HTTPException(status_code=400, detail="TxCreate schema cannot provide amount_oc_secondary and currency_secondary")
    
    # Convert currencies to uppercase
    tx.currency_primary = tx.currency_primary.upper()
    if is_forex_declared:
        tx.currency_secondary = tx.currency_secondary.upper()

def _build_postings_from_tx_input(tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> list[schemas.TxPostingCreateAutomatic]:
    """
    Build the two posting *requests* from the transaction header.
    - For normal transactions: the secondary leg is created with only the account_id.
      Amount/currency will be mirrored later by _validate_and_complete_postings.
    - For forex transactions: both legs include explicit amount + currency.
    """
    # Primary leg always explicit
    primary = schemas.TxPostingCreateAutomatic(
        account_id=tx.account_id_primary,
        amount_oc=tx.amount_oc_primary,
        currency=tx.currency_primary,
        fx_rate=None,
        amount_hc=None
    )
    
    # Forex: user provides destination account and amount (second posting)
    if hasattr(tx, "amount_oc_secondary") and hasattr(tx, "currency_secondary"):
        secondary = schemas.TxPostingCreateAutomatic(
            account_id=tx.account_id_secondary,
            amount_oc=tx.amount_oc_secondary,
            currency=tx.currency_secondary,
            fx_rate=None,
            amount_hc=None
        )
    else:
        secondary = schemas.TxPostingCreateAutomatic(
            account_id=tx.account_id_secondary,
            amount_oc=None,
            currency=None,
            fx_rate=None,
            amount_hc=None
        )
    
    return [primary, secondary]

def _validate_and_complete_postings(db: Session, transaction: models.Transaction, postings: list[schemas.TxPostingCreateAutomatic]) -> list[models.TxPosting]:
    """
    Validates structure & completes postings:
    - Ensures correct accounts for tx type (income/expense/transfer/cc_payment/forex)
    - For normal tx: mirrors secondary amount/currency if missing
    - Determines posting currency (asset/liability = account currency; income/expense = posting currency)
    - Applies sign via _get_amount_multiplier
    - Computes fx_rate to user's home currency and amount_hc
    - Ensures postings balance in home currency
    Returns ready-to-persist models.TxPosting[]
    """
    # ---- helpers (local, tiny) ----
    def _require(condition: bool, message: str) -> None:
        if not condition:
            raise HTTPException(status_code=400, detail=message)

    # Validate there are exactly two postings
    if not postings or len(postings) != 2:
        raise HTTPException(status_code=400, detail="Exactly two postings are required (origin & destination).")

    # Get user and home currency
    user = get_user(db=db, user_id=transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    home_currency = user.home_currency

    # Validate accounts exist and belong to the user
    account_ids = [posting.account_id for posting in postings]
    accounts: list[models.Account] = get_accounts(db=db, user_id=transaction.user_id, account_ids=account_ids)
    if len(accounts) != len(account_ids):
        raise HTTPException(status_code=404, detail="One or more specified accounts do not exist or do not belong to the user")

    # Create account lookup dict
    acc_by_id: Dict[int, models.Account] = {acc.id: acc for acc in accounts}

    # Validate posting structure based on transaction type
    account1, account2 = acc_by_id[postings[0].account_id], acc_by_id[postings[1].account_id]
    type1, type2 = account1.type, account2.type
    # If the account is asset or liability, it must have the same currency as the transaction currency (TODO)
    tx_type = transaction.type

    # Income transactions
    if tx_type == models.TxType.income:
        # Origin account must be asset, destination account must be income
        _require(type1 == models.AccountType.asset and type2 == models.AccountType.income, "Income transactions require one asset account as origin account and one income account as destination account")
        # Don't validate currencies as both legs share original currency
    
    # Expense transactions
    elif tx_type == models.TxType.expense:
        # Origin account must be asset, destination account must be expense
        _require(type1 == models.AccountType.asset and type2 == models.AccountType.expense, "Expense transactions require one asset account as origin account and one expense account as destination account")
        # Don't validate currencies as both legs share original currency
    
    # Transfer transactions
    elif tx_type == models.TxType.transfer:
        # Both accounts must be asset accounts
        _require(type1 == models.AccountType.asset and type2 == models.AccountType.asset, "Transfer transactions require two asset accounts")
        # Both accounts must have the same currency
        _require(account1.currency.upper() == account2.currency.upper(), "Transfer transactions require two accounts with the same currency")

    # Credit card payment transactions
    elif tx_type == models.TxType.credit_card_payment:
        # Origin account must be asset, destination account must be liability
        _require(type1 == models.AccountType.asset and type2 == models.AccountType.liability, "Credit card payment transactions require one asset as origin account and one liability account as destination account")
        # Same currency for both legs
        _require(account1.currency.upper() == account2.currency.upper(), "Credit card payment transactions require two accounts with the same currency")

    # Forex transactions
    elif tx_type == models.TxType.forex:
        # Both accounts must be asset accounts
        _require(type1 == models.AccountType.asset and type2 == models.AccountType.asset, "Forex transactions require two asset accounts")
        # Both accounts must have different currencies
        _require(account1.currency.upper() != account2.currency.upper(), "Forex transactions require two accounts with different currencies")

    else:
        # All other transaction types are not supported
        raise HTTPException(status_code=400, detail=f"Unsupported transaction type: {tx_type}")

    # Fill missing secondary leg info for NORMAL tx (not forex)
    is_forex = (tx_type == models.TxType.forex)
    if not is_forex:
        # Mirror amount_oc from primary leg to secondary leg
        postings[1].amount_oc = postings[0].amount_oc
        # Mirror currency from primary leg to secondary leg
        postings[1].currency = postings[0].currency

    # Build completed postings with signs, currencies, fx_rate and amount_hc
    completed_postings: list[models.TxPosting] = []

    for idx, posting in enumerate(postings):
        account = acc_by_id[posting.account_id]
        sign = _get_amount_multiplier(tx_type, account.type, idx)

        # Validate for asset and liability accounts that the posting currency matches the account currency
        if account.type in [models.AccountType.asset, models.AccountType.liability]:
            if posting.currency != account.currency:
                raise HTTPException(status_code=400, detail=f"Posting currency '{posting.currency}' does not match account currency '{account.currency}' for account '{account.name}'")

        # Determine the amount signed in original currency
        amount_oc_signed = float(posting.amount_oc) * float(sign)

        # FX to home currency and amount in home currency
        if posting.currency == home_currency:
            fx_rate = 1.0
        else:
            fx_rate_obj = get_fx_rate_by_key(db=db, from_currency=posting.currency, to_currency=home_currency, year=transaction.date.year, month=transaction.date.month)
            if not fx_rate_obj:
                raise HTTPException(status_code=404, detail=f"FX rate not found for {posting.currency} to {home_currency}")
            fx_rate = fx_rate_obj.rate
        
        amount_hc = amount_oc_signed * fx_rate

        # Create the posting
        completed_postings.append(models.TxPosting(
            tx_id=transaction.id,
            account_id=account.id,
            amount_oc=amount_oc_signed,
            currency=posting.currency,
            fx_rate=fx_rate,
            amount_hc=amount_hc
        ))
    
    # Balance check in home currency
    total_hc = sum(p.amount_hc for p in completed_postings)
    if not isclose(total_hc, 0.0, rel_tol=0.0, abs_tol=BALANCE_ABS_TOL):
        raise HTTPException(status_code=400, detail="Postings must balance to zero in home currency")
    
    return completed_postings

def _derive_transaction_primary_fields(db: Session, transaction: models.Transaction, completed_postings: list[models.TxPosting]) -> tuple[float, float, str]:
    """
    Derive the primary fields of a transaction from the first posting.
    """
    if not completed_postings or len(completed_postings) < 1:
        raise HTTPException(status_code=400, detail="No postings provided")

    # Load user's home currency
    user = get_user(db=db, user_id=transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    home_currency = user.home_currency

    origin = completed_postings[0]
    origin_currency = origin.currency.upper()
    if origin_currency == home_currency:
        fx_rate = 1.0
    else:
        if origin.fx_rate and origin.fx_rate > 0:
            fx_rate = origin.fx_rate
        else:
            fx_rate_obj = get_fx_rate_by_key(db=db, from_currency=origin_currency, to_currency=home_currency, year=transaction.date.year, month=transaction.date.month)
            if not fx_rate_obj:
                raise HTTPException(status_code=404, detail=f"FX rate not found for {origin_currency} to {home_currency}")
            fx_rate = fx_rate_obj.rate

    amount_oc_primary = abs(float(origin.amount_oc))
    if origin.amount_hc not in (None, 0):
        amount_hc_primary = abs(float(origin.amount_hc))
    else:
        amount_hc_primary = abs(float(amount_oc_primary) * float(fx_rate))
    currency_primary = origin_currency

    return amount_hc_primary, amount_oc_primary, currency_primary

def _get_amount_multiplier(tx_type: models.TxType, account_type: models.AccountType, posting_index: int) -> float:
    if tx_type == models.TxType.income:
        if account_type == models.AccountType.income:
            return -1.0
        elif account_type == models.AccountType.asset:
            return 1.0
        else:
            raise HTTPException(status_code=400, detail="Income transactions require one income account and one asset account")
    
    elif tx_type == models.TxType.expense:
        if account_type == models.AccountType.expense:
            return 1.0
        elif account_type == models.AccountType.asset:
            return -1.0
        else:
            raise HTTPException(status_code=400, detail="Expense transactions require one expense account and one asset account")
    
    elif tx_type == models.TxType.transfer:
        if account_type == models.AccountType.asset:
            return 1.0 if posting_index == 0 else -1.0
        else:
            raise HTTPException(status_code=400, detail="Transfer transactions require two asset accounts")
    
    elif tx_type == models.TxType.credit_card_payment:
        if account_type == models.AccountType.liability:
            return 1.0
        elif account_type == models.AccountType.asset:
            return -1.0
        else:
            raise HTTPException(status_code=400, detail="Credit card payment transactions require one asset account and one liability account")
    
    elif tx_type == models.TxType.forex:
        if account_type == models.AccountType.asset:
            return 1.0 if posting_index == 0 else -1.0
        else:
            raise HTTPException(status_code=400, detail="Forex transactions require two asset accounts")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported transaction type")

#--------------------------------
# User
#--------------------------------
def get_users(db: Session, user_ids: list[int] | None = None) -> list[models.User]:
    query = db.query(models.User).filter(models.User.active == True)
    if user_ids:
        query = query.filter(models.User.id.in_(user_ids))
    return query.all()

def get_user(db: Session, user_id: int) -> models.User | None:
    query = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.active == True
    )
    return query.first()

def get_user_any_status(db: Session, user_id: int) -> models.User | None:
    """Get user by ID regardless of active status."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    _validate_unique_user(db=db, email=user.email)
    db_user = models.User(
        name=user.name,
        email=user.email,
        home_currency=user.home_currency.upper()
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate) -> models.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    _validate_unique_user(db=db, email=user.email, exclude_id=user_id)
    for key, value in user.model_dump(exclude_unset=True).items():
        if key == "home_currency" and value is not None:
            value = value.upper()
        setattr(db_user, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int) -> None:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Validate that there is at least one user active
    if db.query(models.User).filter(models.User.active == True).count() == 1:
        raise HTTPException(status_code=400, detail="Cannot deactivate last active user")
    db_user.active = False
    db_user.deleted_at = datetime.now()
    db.commit()

def activate_user(db: Session, user_id: int) -> None:
    db_user = get_user_any_status(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.active:
        raise HTTPException(status_code=404, detail="User not found")  # Already active, treat as not found
    db_user.active = True
    db_user.deleted_at = None
    db.commit()

#--------------------------------
# People
#--------------------------------
def get_people(db: Session, user_id: int, person_ids: list[int] | None = None) -> list[models.Person]:
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.active == True
    )
    if person_ids:
        query = query.filter(models.Person.id.in_(person_ids))
    return query.all()

def get_all_people(db: Session) -> list[models.Person]:
    """Get all active people regardless of user."""
    return db.query(models.Person).filter(models.Person.active == True).all()

def get_person(db: Session, user_id: int, person_id: int) -> models.Person | None:
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.id == person_id,
        models.Person.active == True
    )
    return query.first()

def get_person_any_status(db: Session, person_id: int) -> models.Person | None:
    """Get person by ID regardless of active status."""
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_person_by_id(db: Session, person_id: int) -> models.Person | None:
    """Get active person by ID regardless of user."""
    return db.query(models.Person).filter(
        models.Person.id == person_id,
        models.Person.active == True
    ).first()

def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    _validate_unique_person(db=db, user_id=person.user_id, name=person.name, is_me=person.is_me)
    db_person = models.Person(
        user_id=person.user_id,
        name=person.name,
        is_me=person.is_me,
    )
    db.add(db_person)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def update_person(db: Session, user_id: int, person_id: int, person: schemas.PersonUpdate) -> models.Person:
    db_person = get_person(db, user_id, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    _validate_unique_person(db=db, user_id=user_id, name=person.name, is_me=person.is_me, exclude_id=person_id)
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def update_person_by_id(db: Session, person_id: int, person: schemas.PersonUpdate) -> models.Person:
    """Update person by ID regardless of user."""
    db_person = get_person_by_id(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    _validate_unique_person(db=db, user_id=db_person.user_id, name=person.name, is_me=person.is_me, exclude_id=person_id)
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def deactivate_person(db: Session, user_id: int, person_id: int) -> models.Person:
    db_person = get_person(db=db, user_id=user_id, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    db_person.active = False
    db_person.deleted_at = datetime.now()
    db.commit()
    db.refresh(db_person)
    return db_person

def activate_person(db: Session, user_id: int, person_id: int) -> models.Person:
    db_person = get_person_any_status(db=db, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    if db_person.active:
        raise HTTPException(status_code=404, detail="Person not found")  # Already active, treat as not found
    db_person.active = True
    db_person.deleted_at = None
    db.commit()
    db.refresh(db_person)
    return db_person
#--------------------------------
# Account
#--------------------------------
def get_accounts(db: Session, user_id: int, account_ids: list[int] | None = None) -> list[models.Account]:
    query = db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.active == True
    )
    if account_ids:
        query = query.filter(models.Account.id.in_(account_ids))
    return query.all()

def get_account(db: Session, user_id: int, account_id: int) -> models.Account | None:
    query = db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.id == account_id,
        models.Account.active == True
    )
    return query.first()

def get_account_any_status(db: Session, user_id: int, account_id: int) -> models.Account | None:
    """Get account by ID regardless of active status."""
    return db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.id == account_id
    ).first()

def create_account(db: Session, account: Union[schemas.AccountCreateIncomeExpense, schemas.AccountCreateAsset, schemas.AccountCreateLiability]) -> models.Account:
    # Validations
    _validate_unique_account(db=db, user_id=account.user_id, name=account.name, type=account.type)
    _validate_account_header(account=account)

    # Create account
    db_account = models.Account(
        user_id=account.user_id,
        name=account.name,
        type=account.type,
        currency=getattr(account, "currency", None),    
        opening_balance=getattr(account, "opening_balance", None),
        current_balance=getattr(account, "opening_balance", None),
        bank_name=getattr(account, "bank_name", None),
        billing_day=getattr(account, "billing_day", None),
        due_day=getattr(account, "due_day", None)
    )
    db.add(db_account)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_account)
    return db_account

#TODO: revisar si es necesario hacer el UNION como en create_account
def update_account(db: Session, user_id: int, account_id: int, account: schemas.AccountUpdate) -> models.Account:
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    _validate_unique_account(db=db, user_id=user_id, name=account.name, type=account.type, exclude_id=account_id)
    _validate_account_update(account=account, current_account=db_account)

    for key, value in account.model_dump(exclude_unset=True).items():
        setattr(db_account, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_account)
    return db_account

def deactivate_account(db: Session, user_id: int, account_id: int) -> models.Account:
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.active = False
    db_account.deleted_at = datetime.now()
    db.commit()
    db.refresh(db_account)
    return db_account

def activate_account(db: Session, user_id: int, account_id: int) -> models.Account:
    db_account = get_account_any_status(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    if db_account.active:
        raise HTTPException(status_code=404, detail="Account not found")  # Already active, treat as not found
    db_account.active = True
    db_account.deleted_at = None
    db.commit()
    db.refresh(db_account)
    return db_account

#--------------------------------
# FX Rate
#--------------------------------
def get_fx_rate_by_id(db: Session, fx_rate_id: int) -> models.FxRate | None:
    query = db.query(models.FxRate).filter(
        models.FxRate.id == fx_rate_id
    )
    return query.first()

def get_fx_rate_by_key(db: Session, from_currency: str, to_currency: str, year: int, month: int) -> models.FxRate | None:
    query = db.query(models.FxRate).filter(
        models.FxRate.from_currency == from_currency,
        models.FxRate.to_currency == to_currency,
        models.FxRate.year == year,
        models.FxRate.month == month
    )
    return query.first()

def create_fx_rate(db: Session, fx_rate: schemas.FxRateCreate) -> models.FxRate:
    db_fx_rate = models.FxRate(
        from_currency=fx_rate.from_currency,
        to_currency=fx_rate.to_currency,
        rate=fx_rate.rate,
        year=fx_rate.year,
        month=fx_rate.month
    )
    db.add(db_fx_rate)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_fx_rate)
    return db_fx_rate

def update_fx_rate_by_key(db: Session, from_currency: str, to_currency: str, year: int, month: int, fx_rate: schemas.FxRateUpdate) -> models.FxRate:
    db_fx_rate = get_fx_rate_by_key(db, from_currency, to_currency, year, month)
    if not db_fx_rate:
        raise HTTPException(status_code=404, detail="FX rate not found")
    for key, value in fx_rate.model_dump(exclude_unset=True).items():
        setattr(db_fx_rate, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_fx_rate)
    return db_fx_rate

#--------------------------------
# Transaction
#--------------------------------
def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[models.Transaction]:
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id, 
        models.Transaction.active == True
    ).order_by(models.Transaction.date.desc())
    return query.offset(skip).limit(limit).all()

def get_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction | None:
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.id == transaction_id,
        models.Transaction.active == True
    )
    return query.first()
    
def create_transaction(db: Session, tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> models.Transaction:
    # Header-level validation
    _validate_tx_header(tx)

    # Create transaction header
    db_tx = models.Transaction(
        user_id=tx.user_id,
        date=tx.date,
        type=tx.type,
        description=tx.description,
        source=tx.source,
        # Primary leg
        account_id_primary=tx.account_id_primary,
        amount_oc_primary=tx.amount_oc_primary,
        currency_primary=tx.currency_primary,
        
        # Secondary leg
        account_id_secondary=tx.account_id_secondary,
        # Forex extra fields
        amount_oc_secondary=getattr(tx, "amount_oc_secondary", None),
        currency_secondary=getattr(tx, "currency_secondary", None)
    )
    db.add(db_tx)
    # Flush to get the transaction ID
    db.flush()

    # Build postings from header and validate
    postings = _build_postings_from_tx_input(tx)

    # Validate and complete postings
    completed_postings = _validate_and_complete_postings(db, db_tx, postings)

    # Attach postings 
    db_tx.postings.extend(completed_postings)

    # Calculate derived values for tx from first posting
    amount_hc_primary, amount_oc_primary, currency_primary = _derive_transaction_primary_fields(db, db_tx, completed_postings)
    db_tx.tx_amount_hc = amount_hc_primary
    db_tx.amount_oc_primary = abs(amount_oc_primary)
    db_tx.currency_primary = currency_primary

    # Commit transaction
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_tx)
    return db_tx

#TODO: revisar si es necesario hacer el UNION como en create_transaction
def update_transaction(db: Session, user_id: int, transaction_id: int, transaction: schemas.TxUpdate):
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in transaction.model_dump(exclude_unset=True).items():
        # Do not update the postings and splits, they are updated separately
        if key not in ("postings", "splits"):
            setattr(db_tx, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_tx)
    return db_tx

def deactivate_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction:
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    now = datetime.now()
    db_tx.active = False
    db_tx.deleted_at = now
    for posting in db_tx.postings:
        posting.active = False
        posting.deleted_at = now
    for split in db_tx.splits:
        split.active = False
        split.deleted_at = now
    db.commit()
    db.refresh(db_tx)
    return db_tx

def activate_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction:
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    now = datetime.now()
    db_tx.active = True
    db_tx.deleted_at = None
    for posting in db_tx.postings:
        posting.active = True
        posting.deleted_at = None
    for split in db_tx.splits:
        split.active = True
        split.deleted_at = None
    db.commit()
    db.refresh(db_tx)
    return db_tx

#--------------------------------
# Posting
#--------------------------------
def get_postings(db: Session, transaction_id: int) -> list[models.TxPosting]:
    query = db.query(models.TxPosting).filter(
        models.TxPosting.tx_id == transaction_id,
    )
    return query.all()

def get_posting(db: Session, posting_id: int) -> models.TxPosting | None:
    query = db.query(models.TxPosting).filter(
        models.TxPosting.id == posting_id,
    )
    return query.first()

#--------------------------------
# TransactionSplit
#--------------------------------
def get_splits(db: Session, transaction_id: int) -> list[models.TxSplit]:
    query = db.query(models.TxSplit).filter(
        models.TxSplit.transaction_id == transaction_id,
    )
    return query.all()

def get_split(db: Session, split_id: int) -> models.TxSplit | None:
    query = db.query(models.TxSplit).filter(
        models.TxSplit.id == split_id,
    )
    return query.first()

#--------------------------------
# Budget
#--------------------------------
def get_budget_month(db: Session, user_id: int, budget_id: int, month: int) -> list[models.BudgetLine] | None:
    query = db.query(models.BudgetLine).join(models.BudgetHeader).filter(
        models.BudgetHeader.id == budget_id,
        models.BudgetHeader.user_id == user_id,
        models.BudgetLine.month == month
    )
    return query.all()

def get_budget(db: Session, user_id: int, budget_id: int) -> list[models.BudgetLine] | None:
    "Get all the lines for a given budget"

    query = db.query(models.BudgetLine).join(models.BudgetHeader).filter(
        models.BudgetHeader.id == budget_id,
        models.BudgetHeader.user_id == user_id
    )
    return query.all()

def create_budget(db: Session, user_id: int, budget: schemas.BudgetCreate) -> models.BudgetHeader:

    # Validate that all accounts exist and currencies match
    for line in budget.lines:
        account = get_account(db, user_id, line.account_id)
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {line.account_id} not found")
        if account.currency != line.currency:
            raise HTTPException(
                status_code=400, 
                detail=f"Currency mismatch: account {account.name} uses {account.currency}, but budget line specifies {line.currency}"
            )

    # Create budget header
    db_budget_header = models.BudgetHeader(
        name=budget.name,
        year=budget.year,
        user_id=user_id
    )
    db.add(db_budget_header)

    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    
    # Create budget lines
    budget_lines = []
    for line in budget.lines:
        db_budget_line = models.BudgetLine(
            month=line.month,
            amount_oc=line.amount_oc,
            currency=line.currency,
            amount_hc=line.amount_hc,
            fx_rate=line.fx_rate,
            description=line.description,
            header_id=db_budget_header.id,
            account_id=line.account_id
        )
        db.add(db_budget_line)
        budget_lines.append(db_budget_line)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")

    db.refresh(db_budget_header)
    return db_budget_header

def update_budget(db: Session, user_id: int, budget_id: int, budget: schemas.BudgetUpdate) -> models.BudgetHeader:
    
    # Get the existing budget header
    db_budget_header = get_budget(db, user_id, budget_id)
    if not db_budget_header:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Update header fields if provided
    if budget.name is not None:
        db_budget_header.name = budget.name
    if budget.year is not None:
        db_budget_header.year = budget.year
    
    # Validate all accounts and currencies for the lines
    for line in budget.lines:
        account = get_account(db, user_id, line.account_id)
        if not account:
            raise HTTPException(status_code=404, detail=f"Account {line.account_id} not found")
        if account.currency != line.currency:
            raise HTTPException(
                status_code=400, 
                detail=f"Currency mismatch: account {account.name} uses {account.currency}, but budget line specifies {line.currency}"
            )
    
    # Handle budget lines - this is a full replacement approach
    # First, delete existing lines
    db.query(models.BudgetLine).filter(
        models.BudgetLine.header_id == budget_id
    ).delete()
    
    # Create new budget lines
    for line in budget.lines:
        db_budget_line = models.BudgetLine(
            month=line.month,
            amount_oc=line.amount_oc,
            currency=line.currency,
            amount_hc=line.amount_hc,
            fx_rate=line.fx_rate,
            description=line.description,
            header_id=db_budget_header.id,
            account_id=line.account_id
        )
        db.add(db_budget_line)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    
    db.refresh(db_budget_header)
    return db_budget_header

def delete_budget(db: Session, id: int) -> None:
    db_budget = get_annual_budget(db, id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(db_budget)
    db.commit()
    return

#--------------------------------
# Report (por validar)
#--------------------------------
def get_balances(db: Session) -> list[schemas.ReportBalance]:
    balances = []
    accounts = db.query(models.Account).all()
    for account in accounts:
        sum_incomes = db.query(func.sum(models.TxPosting.amount_oc)).filter(
            models.TxPosting.account_id == account.id,
            models.TxPosting.transaction.has(type=models.TxType.income)
        ).scalar() or 0
        sum_expenses = db.query(func.sum(models.TxPosting.amount_oc)).filter(
            models.TxPosting.account_id == account.id,
            models.TxPosting.transaction.has(type=models.TxType.expense)
        ).scalar() or 0
        balance = account.opening_balance + sum_incomes - sum_expenses
        balances.append(schemas.ReportBalance(
            account_id=account.id,
            account_name=account.name,
            balance=balance,
            currency=account.currency
        ))
    return balances

def get_debts(db: Session) -> list[schemas.ReportDebt]:
    debts = []
    people = db.query(models.Person).all()
    for person in people:
        sum_debts = db.query(func.sum(models.TxSplit.share_amount)).filter(
            models.TxSplit.person_id == person.id,
            models.TxSplit.transaction.has(type=models.TxType.expense)
        ).scalar() or 0
        sum_credits = db.query(func.sum(models.TxSplit.share_amount)).filter(
            models.TxSplit.person_id == person.id,
            models.TxSplit.transaction.has(type=models.TxType.income)
        ).scalar() or 0
        debt = sum_debts - sum_credits
        debts.append(schemas.ReportDebt(
            person_id=person.id,
            person_name=person.name,
            debt=debt,
            is_active=debt != 0
        ))
    return debts
    
def get_monthly_budget_progress(db: Session, user_id: int, budget_id: int, year: int, month: int) -> list[schemas.ReportBudgetProgress]:
    """
    Get monthly budget progress report for a specific budget, year, and month.
    Returns budget amount, actual expenses, and progress by account for all budget lines in the home currency.
    """
    # Get all budget lines for the specified budget, year, and month
    budget_lines = db.query(models.Budget).filter(
        models.Budget.id == budget_id,
        models.Budget.user_id == user_id,
        models.Budget.year == year,
        models.Budget.month == month
    ).all()
    
    if not budget_lines:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    progress_reports = []
    
    for budget_line in budget_lines:
        # Get all postings for this budget line's account in the specified month
        postings = db.query(models.TxPosting).join(
            models.Transaction, models.TxPosting.tx_id == models.Transaction.id
        ).filter(
            models.TxPosting.account_id == budget_line.account_id,
            models.Transaction.date >= start_date,
            models.Transaction.date < end_date,
            models.Transaction.active == True
        ).all()
        
        # Calculate total actual amount in home currency
        total_actual_hc = sum(posting.amount_hc for posting in postings)
        
        # Calculate progress (actual / budget) - using home currency for comparison
        progress = (total_actual_hc / budget_line.amount_hc) if budget_line.amount_hc > 0 else 0.0
        
        # Get account name
        account = get_account(db, user_id, budget_line.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        progress_reports.append(schemas.ReportBudgetProgress(
            account_id=budget_line.account_id,
            account_name=account.name,
            budget_hc=budget_line.amount_hc,
            actual_hc=total_actual_hc,
            progress=progress
        ))
    
    return progress_reports