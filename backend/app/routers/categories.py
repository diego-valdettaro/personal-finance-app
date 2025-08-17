from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/categories", tags=["categories"])

# Create a category
@router.post("/", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

# List all categories
@router.get("/", response_model=list[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

# Get a category
@router.get("/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return crud.get_category(db, category_id)

# Update a category
@router.patch("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, category: schemas.CategoryUpdate, db:Session = Depends(get_db)):
    return crud.update_category(db, category_id, category)

# Delete a category
@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    crud.delete_category(db, category_id)
    return
