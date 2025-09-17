"""
Transactions CRUD operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import Union

from .. import models, schemas
from .common import _validate_tx_header, _build_postings_from_tx_input, _validate_and_complete_postings, _derive_transaction_primary_fields

def get_transactions(db: Session, user_id: int = None, skip: int = 0, limit: int = 50, date_from: str = None, date_to: str = None, account_id: int = None, category_id: int = None, payer_person_id: int = None) -> list[models.Transaction]:
    """Get all active transactions for a user with pagination."""
    query = db.query(models.Transaction).filter(models.Transaction.active == True)
    if user_id is not None:
        query = query.filter(models.Transaction.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_id: int, user_id: int = None) -> models.Transaction:
    """Get a single active transaction by ID for a specific user."""
    query = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.active == True
    )
    if user_id is not None:
        query = query.filter(models.Transaction.user_id == user_id)
    transaction = query.first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

def create_transaction(db: Session, tx: Union[schemas.TxCreate, schemas.TxCreateForex]) -> models.Transaction:
    """Create a new transaction with automatic postings."""
    # Validate transaction header
    _validate_tx_header(tx)
    
    # Create transaction
    db_transaction = models.Transaction(
        user_id=tx.user_id,
        type=tx.type,
        description=tx.description,
        date=tx.date,
        account_id_primary=tx.account_id_primary,
        amount_oc_primary=tx.amount_oc_primary,
        currency_primary=tx.currency_primary,
        account_id_secondary=tx.account_id_secondary,
        amount_oc_secondary=getattr(tx, 'amount_oc_secondary', None),
        currency_secondary=getattr(tx, 'currency_secondary', None)
    )
    db.add(db_transaction)
    
    try:
        db.flush()  # Get the transaction ID
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Constraint violation: {e.orig}")
    
    # Build and validate postings
    postings_data = _build_postings_from_tx_input(tx)
    completed_postings = _validate_and_complete_postings(db, db_transaction, postings_data)
    
    # Set transaction amount to primary amount
    db_transaction.tx_amount_hc = tx.amount_oc_primary
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TxUpdate, user_id: int = None):
    """Update an existing transaction and its postings."""
    db_transaction = get_transaction(db=db, user_id=user_id, transaction_id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if any posting-related fields are being updated
    update_data = transaction.model_dump(exclude_unset=True)
    posting_related_fields = {'type', 'amount_oc_primary', 'currency_primary', 'account_id_primary', 
                             'account_id_secondary', 'amount_oc_secondary', 'currency_secondary'}
    
    needs_posting_update = any(field in update_data for field in posting_related_fields)
    
    # Update transaction fields
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    try:
        # If posting-related fields were updated, rebuild postings
        if needs_posting_update:
            # Deactivate existing postings
            existing_postings = db.query(models.TxPosting).filter(
                models.TxPosting.tx_id == transaction_id,
                models.TxPosting.active == True
            ).all()
            
            for posting in existing_postings:
                posting.active = False
            
            # Commit the deactivation first
            db.commit()
            
            # Create new postings based on updated transaction data
            # We need to create a temporary transaction object for posting generation
            temp_tx_data = {
                'user_id': db_transaction.user_id,
                'type': db_transaction.type,
                'description': db_transaction.description,
                'date': db_transaction.date,
                'account_id_primary': db_transaction.account_id_primary,
                'amount_oc_primary': db_transaction.amount_oc_primary,
                'currency_primary': db_transaction.currency_primary,
                'account_id_secondary': db_transaction.account_id_secondary,
                'amount_oc_secondary': db_transaction.amount_oc_secondary,
                'currency_secondary': db_transaction.currency_secondary
            }
            
            # Create appropriate schema object based on transaction type
            if db_transaction.type == models.TxType.forex:
                temp_tx = schemas.TxCreateForex(**temp_tx_data)
            else:
                temp_tx = schemas.TxCreate(**temp_tx_data)
            
            # Build and validate new postings
            postings_data = _build_postings_from_tx_input(temp_tx)
            completed_postings = _validate_and_complete_postings(db, db_transaction, postings_data)
            
            # Update transaction amount
            db_transaction.tx_amount_hc = db_transaction.amount_oc_primary
        
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_transaction)
    return db_transaction

def deactivate_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction:
    """Deactivate a transaction (soft delete) and its postings."""
    # Get transaction without filtering by active status
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == user_id,
        models.Transaction.active == True  # Only deactivate if currently active
    ).first()
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Deactivate the transaction
    db_transaction.active = False
    
    # Deactivate all associated postings
    postings = db.query(models.TxPosting).filter(
        models.TxPosting.tx_id == transaction_id,
        models.TxPosting.active == True
    ).all()
    
    for posting in postings:
        posting.active = False
    
    db.commit()
    return db_transaction

def activate_transaction(db: Session, user_id: int, transaction_id: int) -> models.Transaction:
    """Activate a transaction and its postings."""
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == user_id
    ).first()
    
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if db_transaction.active:
        raise HTTPException(status_code=404, detail="Transaction is already active")
    
    # Activate the transaction
    db_transaction.active = True
    
    # Activate all associated postings
    postings = db.query(models.TxPosting).filter(
        models.TxPosting.tx_id == transaction_id,
        models.TxPosting.active == False
    ).all()
    
    for posting in postings:
        posting.active = True
    
    db.commit()
    return db_transaction

