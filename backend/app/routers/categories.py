from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/categories", tags=["categories"])

# Create a category
@router.post("/", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    return crud.create_category(db, category)

# List all categories
@router.get("/", response_model=list[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    db_categories = crud.get_categories(db)
    if not db_categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return db_categories

# Get a category
@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# Update a category
@router.patch("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, category: schemas.CategoryUpdate, db:Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.update_category(db, category_id, category)

# Delete a category
@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    crud.delete_category(db, category_id)
    return
