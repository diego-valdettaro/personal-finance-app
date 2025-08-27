from datetime import date

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from math import isfinite
from typing import Union

from . import models, schemas

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

def _validate_and_complete_postings(db: Session, transaction: models.Transaction, postings: list[schemas.TxPostingCreateAutomatic]) -> list[models.TxPosting]:
    if not postings:
        raise HTTPException(status_code=400, detail="Accounts involved not provided")

    # Get user
    user = db.get(models.User, transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate accounts
    account_ids = [posting.account_id for posting in postings]
    accounts = db.query(models.Account).filter(
        models.Account.id.in_(account_ids),
        models.Account.user_id == transaction.user_id,
        models.Account.active == True
    ).all()
    if len(accounts) != len(account_ids):
        raise HTTPException(status_code=404, detail="One or more specified accounts do not exist or do not belong to the user")

    # Create account lookup
    account_lookup = {acc.id: acc for acc in accounts}

    # Validate posting structure based on transaction type
    if transaction.type == models.TxType.income:
        if len(postings) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Income transactions require exactly 2 postings: one income account and one asset account"
            )
        
        # Validate account types
        income_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.income]
        asset_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.asset]
        
        if not income_accounts or not asset_accounts:
            raise HTTPException(
                status_code=400, 
                detail="Income transactions require one income account and one asset account"
            )
    
    elif transaction.type == models.TxType.expense:
        if len(postings) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Expense transactions require exactly 2 postings: one expense account and one asset account"
            )
        
        # Validate account types
        expense_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.expense]
        asset_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.asset]
        
        if not expense_accounts or not asset_accounts:
            raise HTTPException(
                status_code=400, 
                detail="Expense transactions require one expense account and one asset account"
            )
    
    elif transaction.type == models.TxType.transfer:
        if len(postings) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Transfer transactions require exactly 2 postings: two asset accounts"
            )
        
        # Validate account types
        asset_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.asset]
        
        if len(asset_accounts) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Transfer transactions require two asset accounts"
            )

        # Validate same currency for both accounts
        if postings[0].currency != postings[1].currency:
            raise HTTPException(
                status_code=400, 
                detail="Transfer transactions require two accounts with the same currency"
            )
    
    elif transaction.type == models.TxType.credit_card_payment:
        if len(postings) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Credit card payment transactions require exactly 2 postings: one liability account and one asset account"
            )
        
        # Validate account types
        liability_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.liability]
        asset_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.asset]
        
        if not liability_accounts or not asset_accounts:
            raise HTTPException(
                status_code=400, 
                detail="Credit card payment transactions require one liability account and one asset account"
            )

        # Validate same currency for both accounts
        if postings[0].currency != postings[1].currency:
            raise HTTPException(
                status_code=400, 
                detail="Credit card payment transactions require two accounts with the same currency"
            )

    elif transaction.type == models.TxType.forex:
        if len(postings) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Forex transactions require exactly 2 postings: two asset accounts"
            )
        
        # Validate account types
        asset_accounts = [p for p in postings if account_lookup[p.account_id].type == models.AccountType.asset]
        
        if len(asset_accounts) != 2:
            raise HTTPException(
                status_code=400, 
                detail="Forex transactions require two asset accounts"
            )

        # Validate different currencies for both accounts
        if postings[0].currency == postings[1].currency:
            raise HTTPException(
                status_code=400, 
                detail="Forex transactions require two accounts with different currencies"
            )
    
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported transaction type: {transaction.type}"
        )
    
    # Complete posting details
    completed_postings = []
    for i, posting in enumerate(postings):
        account = account_lookup[posting.account_id]

        # Get the sign of the posting based on the transaction type and account type
        sign = _get_amount_multiplier(transaction.type, account.type, i)

        # Determine currency based on account type
        if account.type in [models.AccountType.asset, models.AccountType.liability]:
            # For asset and liability accounts, use the account's currency
            currency = account.currency
            if posting.currency and posting.currency != currency:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Posting currency '{posting.currency}' does not match account currency '{currency}' for account '{account.name}'"
                )
        else:
            # For income and expense accounts, use the posting's currency
            currency = posting.currency
            if not currency:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Currency must be specified for {account.type} account '{account.name}'"
                )

        # Calculate fx_rate for forex transactions
        fx_rate = 1.0
        if transaction.type == models.TxType.forex and i == 1:
            #Calculate fx_rate based on the two amounts provided
            amount1 = postings[0].amount_oc
            amount2 = posting.amount_oc
            if amount1 != 0:
                fx_rate = abs(amount2 / amount1)

        completed_posting = models.TxPosting(
            transaction_id=transaction.id,
            account_id=posting.account_id,
            amount_oc=posting.amount_oc * sign,
            currency=currency,
            fx_rate=fx_rate,
            amount_hc=posting.amount_oc * sign * fx_rate
        )
        completed_postings.append(completed_posting)
    
    # Validate that postings sum zero
    total_amount = sum(posting.amount_hc for posting in completed_postings)
    if abs(total_amount) > 0.000001:
        raise HTTPException(status_code=400, detail="The sum of the postings must sum zero")

    return completed_postings

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
def get_users(db: Session):
    query = db.query(models.User).filter(models.User.active == True)
    return query.all()

def get_user(db: Session, user_id: int):
    query = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.active == True
    )
    return query.first()

def create_user(db: Session, user: schemas.UserCreate):
    _validate_unique_user(db, user.name, user.email)
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

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    _validate_unique_user(db, user.name, user.email, user_id)
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.active = False
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.active = True
    db.commit()
    db.refresh(db_user)
    return db_user

#--------------------------------
# People
#--------------------------------
def get_people(db: Session, user_id: int):
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.active == True
    )
    return query.all()

def get_person(db: Session, user_id: int, person_id: int):
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.id == person_id,
        models.Person.active == True
    )
    return query.first()

def create_person(db: Session, person: schemas.PersonCreate):
    _validate_unique_person(db, person.name, person.is_me, person.user_id)
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

def update_person(db: Session, user_id: int, person_id: int, person: schemas.PersonUpdate):
    db_person = get_person(db, user_id, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    _validate_unique_person(db, person.name, person.is_me, user_id, person_id)
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def deactivate_person(db: Session, user_id: int, person_id: int):
    db_person = get_person(db, user_id, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    db_person.active = False
    db.commit()
    db.refresh(db_person)
    return db_person

def activate_person(db: Session, user_id: int, person_id: int):
    db_person = get_person(db, user_id, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    db_person.active = True
    db.commit()
    db.refresh(db_person)
    return db_person
#--------------------------------
# Account
#--------------------------------
def get_accounts(db: Session, user_id: int):
    query = db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.active == True
    )
    return query.all()

def get_account(db: Session, user_id: int, account_id: int):
    query = db.query(models.Account).filter(
        models.Account.user_id == user_id,
        models.Account.id == account_id,
        models.Account.active == True
    )
    return query.first()

def create_account(db: Session, account: schemas.AccountCreate):
    _validate_unique_account(db, account.name, account.user_id)

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

def update_account(db: Session, user_id: int, account_id: int, account: schemas.AccountUpdate):
    db_account = get_account(db, user_id, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    _validate_unique_account(db, account.name, user_id, account_id)
    
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

def deactivate_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.active = False
    db.commit()
    db.refresh(db_account)
    return db_account

def activate_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.active = True
    db.commit()
    db.refresh(db_account)
    return db_account

#--------------------------------
# Transaction
#--------------------------------
def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id, 
        models.Transaction.active == True
    ).order_by(models.Transaction.date.desc())
    return query.offset(skip).limit(limit).all()

def get_transaction(db: Session, user_id: int, transaction_id: int):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.id == transaction_id,
        models.Transaction.active == True
    )
    return query.first()
    
def create_transaction(db: Session, tx: Union[schemas.TxCreate, schemas.TxCreateForex]):
    # Header-level validation
    _validate_tx_header(tx)

    # Create transaction header
    db_tx = models.Transaction(
        user_id=tx.user_id,
        date=tx.date,
        type=tx.type,
        description=tx.description,
        source=tx.source,
        amount_oc_primary=tx.amount_oc_primary,
        currency_primary=tx.currency_primary.upper(),
        account_id_primary=tx.account_id_primary,
        account_id_secondary=tx.account_id_secondary

        # Forex extra fields
        amount_oc_secondary=getattr(tx, "amount_oc_secondary", None),
        currency_secondary=getattr(tx, "currency_secondary", None)
    )
    db.add(db_tx)
    # Flush to get the transaction ID
    db.flush()

    # Build postings from header and validate
    postings_in = _build_postings_from_tx_input(tx)
    if not postings_in or len(postings_in) != 2:
        raise HTTPException(status_code=400, detail="Exactly two postings are required (origin & destination).")

    # Validate and complete postings
    completed_postings = _validate_and_complete_postings(db, db_tx, postings_in)

    # Attach postings 
    db_tx.postings.extend(completed_postings)

    # Calculate derived values for tx from first posting
    amount_hc_primary, amount_oc_primary, currency_primary = _derive_transaction_primary_fields(completed_postings)
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

def deactivate_transaction(db: Session, user_id: int, transaction_id: int):
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db_tx.active = False
    db.commit()
    db.refresh(db_tx)
    return db_tx

def activate_transaction(db: Session, user_id: int, transaction_id: int):
    db_tx = get_transaction(db, user_id, transaction_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db_tx.active = True
    db.commit()
    db.refresh(db_tx)
    return db_tx

#--------------------------------
# Posting
#--------------------------------
def get_postings(db: Session, transaction_id: int):
    query = db.query(models.TxPosting).filter(
        models.TxPosting.transaction_id == transaction_id,
    )
    return query.all()

def get_posting(db: Session, posting_id: int):
    query = db.query(models.TxPosting).filter(
        models.TxPosting.id == posting_id,
    )
    return query.first()

def create_posting(db: Session, transaction_id: int, posting: schemas.TxPostingCreate):
    # Validate currency is the same as the account currency
    account = db.query(models.Account).filter(models.Account.id == posting.account_id).first()
    if account.currency != posting.currency:
        raise HTTPException(status_code=400, detail="Currency mismatch between account and posting")
    db_posting = models.TxPosting(
        transaction_id=transaction_id,
        amount_oc=posting.amount_oc,
        currency=posting.currency,
        fx_rate=posting.fx_rate,
        amount_hc=posting.amount_hc,
        account_id=posting.account_id,
    )
    db.add(db_posting)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_posting)
    return db_posting

def update_posting(db: Session, posting_id: int, posting: schemas.TxPostingUpdate):
    db_posting = get_posting(db, posting_id)
    if not db_posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    # Validate currency is the same as the account currency
    account = db.query(models.Account).filter(models.Account.id == db_posting.account_id).first()
    if account.currency != posting.currency:
        raise HTTPException(status_code=400, detail="Currency mismatch between account and posting")
    for key, value in posting.model_dump(exclude_unset=True).items():
        setattr(db_posting, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_posting)
    return db_posting

#--------------------------------
# TransactionSplit
#--------------------------------
def get_splits(db: Session, transaction_id: int):
    query = db.query(models.TransactionSplit).filter(
        models.TransactionSplit.transaction_id == transaction_id,
    )
    return query.all()

def get_split(db: Session, split_id: int):
    query = db.query(models.TransactionSplit).filter(
        models.TransactionSplit.id == split_id,
    )
    return query.first()

def create_split(db: Session, transaction_id: int, split: schemas.TxSplitCreate):
    db_split = models.TransactionSplit(
        transaction_id=transaction_id,
        person_id=split.person_id,
        share_amount=split.share_amount,
    )
    db.add(db_split)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_split)
    return db_split

def update_split(db: Session, split_id: int, split: schemas.TxSplitUpdate):
    db_split = get_split(db, split_id)
    if not db_split:
        raise HTTPException(status_code=404, detail="Transaction split not found")
    for key, value in split.model_dump(exclude_unset=True).items():
        setattr(db_split, key, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_split)
    return db_split

#--------------------------------
# Budget
#--------------------------------
def get_monthly_budget(db: Session, id: int, month: int):
    query = db.query(models.Budget).filter(
        models.Budget.id == id,
        models.Budget.month == month
    )
    return query.first()

def get_annual_budget(db: Session, id: int):
    query = db.query(models.Budget).filter(
        models.Budget.id == id,
    )
    return query.first()

def create_annual_budget(db: Session, budget: schemas.BudgetCreate):
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

def update_annual_budget(db: Session, id: int, budget: schemas.BudgetUpdate):
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

def delete_annual_budget(db: Session, id: int):
    db_budget = get_annual_budget(db, id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(db_budget)
    db.commit()
    return

#--------------------------------
# Report (por validar)
#--------------------------------
def get_balances(db: Session):
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

def get_debts(db: Session):
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
    
def get_budget_progress(db: Session, id: int, month: int):
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

def get_monthly_budget_progress(db: Session, budget_id: int, year: int, month: int):
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

