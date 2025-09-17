"""
Foreign exchange rates CRUD operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .. import models, schemas

def get_fx_rate_by_id(db: Session, fx_rate_id: int) -> models.FxRate | None:
    """Get an FX rate by ID."""
    return db.query(models.FxRate).filter(models.FxRate.id == fx_rate_id).first()

def get_fx_rate_by_key(db: Session, from_currency: str, to_currency: str, year: int, month: int) -> models.FxRate | None:
    """Get an FX rate by currency pair and date."""
    return db.query(models.FxRate).filter(
        models.FxRate.from_currency == from_currency,
        models.FxRate.to_currency == to_currency,
        models.FxRate.year == year,
        models.FxRate.month == month
    ).first()

def create_fx_rate(db: Session, fx_rate: schemas.FxRateCreate) -> models.FxRate:
    """Create a new FX rate."""
    db_fx_rate = models.FxRate(
        from_currency=fx_rate.from_currency,
        to_currency=fx_rate.to_currency,
        year=fx_rate.year,
        month=fx_rate.month,
        rate=fx_rate.rate
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
    """Update an FX rate by currency pair and date."""
    db_fx_rate = get_fx_rate_by_key(db, from_currency, to_currency, year, month)
    if not db_fx_rate:
        raise HTTPException(status_code=404, detail="FX rate not found")
    
    # Update fields
    for key, value in fx_rate.model_dump(exclude_unset=True).items():
        setattr(db_fx_rate, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_fx_rate)
    return db_fx_rate
