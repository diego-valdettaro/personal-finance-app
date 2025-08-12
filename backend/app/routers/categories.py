from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=schemas.CategoryOut)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    if db.query(models.Category).filter(models.Category.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Category name already exists")
    cat = models.Category(name=payload.name, type=payload.type)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.type, models.Category.name).all()

@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(models.Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.patch("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, payload: schemas.CategoryUpdate, db:Session = Depends(get_db)):
    cat = db.get(models.Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        cat.name = payload.name
    if payload.type is not None:
        cat.type = payload.type
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.get(models.Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
