from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=schemas.AccountOut)
def create_account(payload: schemas.AccountCreate, db: Session = Depends(get_db)):
    acc = models.Account(name=payload.name, currency=payload.currency)
    try:
        db.add(acc)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists")
    db.refresh(acc)
    return acc

@router.get("/", response_model=List[schemas.AccountOut])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).order_by(models.Account.name).all()

@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.get(models.Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@router.patch("/{account_id}", response_model=schemas.AccountOut)
def update_account(account_id: int, payload: schemas.AccountUpdate, db: Session = Depends(get_db)):
    acc = db.get(models.Account,account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    if payload.name is not None:
        acc.name = payload.name
    if payload.currency is not None:
        acc.currency = payload.currency
    db.commit()
    db.refresh(acc)
    return acc

@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.get(models.Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(acc)
    db.commit()