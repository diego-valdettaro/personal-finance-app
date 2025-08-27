from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/users", tags=["users"])

# Create a user
@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# List all users
@router.get("/", response_model=list[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

# Get a user
@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)

# Update a user
@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, user)

# Deactivate a user
@router.patch("/{user_id}/deactivate", status_code=204)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    return crud.deactivate_user(db, user_id)

# Activate a user
@router.patch("/{user_id}/activate", status_code=204)
def activate_user(user_id: int, db: Session = Depends(get_db)):
    return crud.activate_user(db, user_id)