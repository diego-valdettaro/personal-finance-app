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
def _validate_unique_user(db: Session, name: str, email: str | None, exclude_id: int | None = None) -> None:
    query = db.query(models.User)
    q = query.filter(models.User.name == name)
    if email:
        q = query.filter(models.User.email == email)
    if exclude_id:
        q = q.filter(models.User.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"User with name {name} or email {email} already exists")

def _validate_unique_person(db: Session, user_id: int, name: str, is_me: bool, exclude_id: int | None = None) -> None:
    query = db.query(models.Person)
    q = query.filter(
        models.Person.user_id == user_id,
        models.Person.name == name
    )
    if exclude_id:
        q = q.filter(models.Person.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"Person with name {name} already exists for user {user_id}")
    if is_me:
        q = q.filter(models.Person.is_me == is_me)
        if q.first():
            raise HTTPException(status_code=409, detail=f"User {user_id} already has a me person defined")

def _validate_unique_account(db: Session, user_id: int, name: str, exclude_id: int | None = None) -> None:
    query = db.query(models.Account)    
    q = query.filter(
        models.Account.user_id == user_id,
        models.Account.name == name
    )
    if exclude_id:
        q = q.filter(models.Account.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=409, detail=f"Account with name {name} already exists for user {user_id}")

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
    fx_rates = get_fx_rates_by_date(db=db, year=transaction.date.year, month=transaction.date.month)

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
        if posting.currency != home_currency:
            fx_rate = 1.0
        else:
            fx_rate = fx_rates[posting.currency][home_currency]
        
        amount_hc = amount_oc_signed * fx_rate

        # Create the posting
        completed_postings.append(models.TxPosting(
            transaction_id=transaction.id,
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
            fx_rate = get_fx_rate(db=db, from_currency=origin_currency, to_currency=home_currency, year=transaction.date.year, month=transaction.date.month)

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
        raise HTTPException(status_code=400, detail="Transfer transactions require two asset accounts")
    
    elif tx_type == models.TxType.credit_card_payment:
        if account_type == models.AccountType.liability:
            return 1.0
        elif account_type == models.AccountType.asset:
            return -1.0
        else:
            # Default to first posting debit, second credit
            return 1.0 if posting_index == 0 else -1.0

    elif tx_type == models.TxType.forex:
        return 1.0 if posting_index == 0 else -1.0
    
    else:
        # Default to first posting debit, second credit
        return 1.0 if posting_index == 0 else -1.0

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

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    _validate_unique_user(db=db, name=user.name, email=user.email)
    db_user = models.User(
        name=user.name,
        email=user.email,
        home_currency=user.home_currency
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
    _validate_unique_user(db=db, name=user.name, email=user.email, exclude_id=user_id)
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int) -> models.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.active = False
    db_user.deleted_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_user(db: Session, user_id: int) -> models.User:
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.active = True
    db_user.deleted_at = None
    db.commit()
    db.refresh(db_user)
    return db_user

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

def get_person(db: Session, user_id: int, person_id: int) -> models.Person | None:
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.id == person_id,
        models.Person.active == True
    )
    return query.first()

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
    db_person = get_person(db=db, user_id=user_id, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
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

def create_account(db: Session, account: schemas.AccountCreate) -> models.Account:
    _validate_unique_account(db=db, user_id=account.user_id, name=account.name)

    # Validate currency based on account type
    if account.type in [models.AccountType.income, models.AccountType.expense, models.AccountType.equity] and account.currency is not None:
        raise HTTPException(status_code=400, detail=f"Currency should not be specified for {account.type} accounts")
    elif account.type in [models.AccountType.asset, models.AccountType.liability] and account.currency is None:
        raise HTTPException(status_code=400, detail=f"Currency is required for {account.type} accounts")
    
    db_account = models.Account(
        user_id=account.user_id,
        name=account.name,
        type=account.type,
        currency=account.currency,    
        opening_balance=account.opening_balance,
        billing_day=account.billing_day,
        due_day=account.due_day
    )
    db.add(db_account)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_account)
    return db_account

def update_account(db: Session, user_id: int, account_id: int, account: schemas.AccountUpdate) -> models.Account:
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    _validate_unique_account(db=db, user_id=user_id, name=account.name, exclude_id=account_id)
    
    # Handle account type changes and currency requirements
    update_data = account.model_dump(exclude_unset=True)
    
    # If account type is being changed, handle currency appropriately
    if 'type' in update_data:
        new_type = update_data['type']
        if new_type in [models.AccountType.income, models.AccountType.expense, models.AccountType.equity]:
            # Clear currency for income/expense/equity accounts
            update_data['currency'] = None
        elif new_type in [models.AccountType.asset, models.AccountType.liability]:
            # Ensure currency is set for asset/liability accounts
            if 'currency' not in update_data or update_data['currency'] is None:
                raise HTTPException(status_code=400, detail=f"Currency is required when changing account type to {new_type}")
    
    for key, value in update_data.items():
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
    db_account = get_account(db=db, user_id=user_id, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.active = True
    db_account.deleted_at = None
    db.commit()
    db.refresh(db_account)
    return db_account

#--------------------------------
# FX Rate
#--------------------------------
def get_fx_rates_by_date(db: Session, year: int, month: int) -> list[models.FxRate]:
    query = db.query(models.FxRate).filter(
        models.FxRate.year == year,
        models.FxRate.month == month
    )
    return query.all()

def get_fx_rate(db: Session, from_currency: str, to_currency: str, year: int, month: int) -> models.FxRate | None:
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

def update_fx_rate(db: Session, fx_rate_id: int, fx_rate: schemas.FxRateUpdate) -> models.FxRate:
    db_fx_rate = get_fx_rate(db, fx_rate_id)
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
    db_tx.amount_hc_primary = amount_hc_primary
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
    db_tx.active = False
    db_tx.deleted_at = datetime.now()
    db.commit()
    db.refresh(db_tx)
    return db_tx

def activate_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction:
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db_tx.active = True
    db_tx.deleted_at = None
    db.commit()
    db.refresh(db_tx)
    return db_tx

#--------------------------------
# Posting
#--------------------------------
def get_postings(db: Session, transaction_id: int) -> list[models.TxPosting]:
    query = db.query(models.TxPosting).filter(
        models.TxPosting.transaction_id == transaction_id,
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
def get_monthly_budget(db: Session, id: int, month: int) -> models.Budget | None:
    query = db.query(models.Budget).filter(
        models.Budget.id == id,
        models.Budget.month == month
    )
    return query.first()

def get_annual_budget(db: Session, id: int) -> models.Budget | None:
    query = db.query(models.Budget).filter(
        models.Budget.id == id,
    )
    return query.first()

def create_annual_budget(db: Session, budget: schemas.BudgetCreate) -> models.Budget:
    # Validate currency is the same as the account currency
    account = db.query(models.Account).filter(models.Account.id == budget.account_id).first()
    if account.currency != budget.currency:
        raise HTTPException(status_code=400, detail="Currency mismatch between account and budget")
    db_budget = models.Budget(
        name=budget.name,
        year=budget.year,
        month=budget.month,
        amount_oc=budget.amount_oc,
        currency=budget.currency,
        amount_hc=budget.amount_hc,
        fx_rate=budget.fx_rate,
        description=budget.description,
        user_id=budget.user_id,
        account_id=budget.account_id
    )
    db.add(db_budget)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_budget)
    return db_budget

def update_annual_budget(db: Session, id: int, budget: schemas.BudgetUpdate) -> models.Budget:
    db_budget = get_annual_budget(db, id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for key, value in budget.model_dump(exclude_unset=True).items():
        setattr(db_budget, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_budget)
    return db_budget

def delete_annual_budget(db: Session, id: int) -> None:
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
    
def get_budget_progress(db: Session, id: int, month: int) -> list[schemas.ReportBudgetProgress]:
    # Get all budgets for the specified month
    budgets = db.query(models.Budget).filter(
        models.Budget.id == id,
        models.Budget.month == month
    ).all()
    
    progress_reports = []
    for budget in budgets:
        try:
            progress_report = get_monthly_budget_progress(db, budget.id, budget.year, budget.month)
            progress_reports.append(progress_report)
        except HTTPException:
            # Skip budgets that can't be processed
            continue
    
    return progress_reports

def get_monthly_budget_progress(db: Session, budget_id: int, year: int, month: int) -> schemas.ReportBudgetProgress:
    """
    Get monthly budget progress report for a specific budget, year, and month.
    Returns budget amount, actual expenses, and progress by account.
    """
    # Get the specific budget
    budget = db.query(models.Budget).filter(
        models.Budget.id == budget_id,
        models.Budget.year == year,
        models.Budget.month == month
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Get all transactions for the budget's account in the specified month
    # We need to join with postings to get transactions for the specific account
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    transactions = db.query(models.Transaction).join(
        models.Posting, models.Transaction.id == models.Posting.transaction_id
    ).filter(
        models.Posting.account_id == budget.account_id,
        models.Transaction.date >= start_date,
        models.Transaction.date < end_date,
        models.Transaction.type == models.TxType.expense,
        models.Transaction.active == True
    ).all()
    
    # Calculate total actual expenses in home currency
    total_actual_hc = sum(transaction.amount_hc for transaction in transactions)
    
    # Calculate progress (actual / budget)
    progress = (total_actual_hc / budget.amount_hc) if budget.amount_hc > 0 else 0.0
    
    # Get account name
    account = db.query(models.Account).filter(models.Account.id == budget.account_id).first()
    account_name = account.name if account else "Unknown Account"
    
    return schemas.ReportBudgetProgress(
        account_id=budget.account_id,
        account_name=account_name,
        budget_hc=budget.amount_hc,
        actual_hc=total_actual_hc,
        progress=progress
    )

