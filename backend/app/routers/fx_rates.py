from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..crud import fx_rates as crud_fx_rates
from ..dependencies import get_authenticated_user
from ..models import User

router = APIRouter(prefix="/fx-rates", tags=["fx-rates"])

@router.post("/", response_model=schemas.FxRateOut, status_code=201)
def create_fx_rate(fx_rate: schemas.FxRateCreate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_fx_rates.create_fx_rate(db, fx_rate)

@router.get("/", response_model=list[schemas.FxRateOut])
def get_fx_rates(db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_fx_rates.get_fx_rates(db)

@router.get("/{fx_rate_id}", response_model=schemas.FxRateOut)
def get_fx_rate(fx_rate_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    fx_rate = crud_fx_rates.get_fx_rate(db, fx_rate_id)
    if not fx_rate:
        raise HTTPException(status_code=404, detail="FX rate not found")
    return fx_rate

@router.patch("/{fx_rate_id}", response_model=schemas.FxRateOut)
def update_fx_rate(fx_rate_id: int, fx_rate: schemas.FxRateUpdate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_fx_rates.update_fx_rate(db, fx_rate_id, fx_rate)

@router.delete("/{fx_rate_id}", status_code=204)
def delete_fx_rate(fx_rate_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_fx_rates.delete_fx_rate(db, fx_rate_id)
    return
