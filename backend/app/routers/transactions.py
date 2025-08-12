from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if not db.get(models.Account, payload.account_id):
        raise HTTPException(status_code=400, detail="Account not found")
    if not db.get(models.Category, payload.category_id):
        raise HTTPException(status_code=400, detail="Category not found")
    tx = models.Transaction(**payload.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

@router.get("/", response_model=List[schemas.TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    q = db.query(models.Transaction)
    if start_date:
        q = q.filter(models.Transaction.date >= start_date)
    if end_date:
        q = q.filter(models.Transaction.date <= end_date)
    return q.order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).offset(offset).limit(limit).all()

@router.get("/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.patch("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(tx, k, v)
    db.commit()
    db.refresh(tx)
    return tx

@router.delete("/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()