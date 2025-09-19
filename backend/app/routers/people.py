from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import people as crud_people
from ..database import get_db
from ..dependencies import get_authenticated_user
from ..models import User

router = APIRouter(prefix="/users/{user_id}/people", tags=["people"])

# Create a person
@router.post("/", response_model=schemas.PersonOut, status_code=201)
def create_person(user_id: int, person: schemas.PersonCreate, db: Session = Depends(get_db)):
    # Ensure person.user_id matches the URL parameter
    if person.user_id != user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    return crud_people.create_person(db, person)
    
# List all people for a user
@router.get("/", response_model=list[schemas.PersonOut])
def get_people(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_people.get_people(db, user_id)

# Get a person
@router.get("/{person_id}", response_model=schemas.PersonOut)
def get_person(user_id: int, person_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    person = crud_people.get_person(db, user_id, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

# Update a person
@router.patch("/{person_id}", response_model=schemas.PersonOut)
def update_person(user_id: int, person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    return crud_people.update_person(db, user_id, person_id, person)

# Deactivate a person
@router.patch("/{person_id}/deactivate", status_code=204)
def deactivate_person(user_id: int, person_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_people.deactivate_person(db, user_id, person_id)
    return None

# Activate a person
@router.patch("/{person_id}/activate", status_code=204)
def activate_person(user_id: int, person_id: int, db: Session = Depends(get_db), user: User = Depends(get_authenticated_user)):
    crud_people.activate_person(db, user_id, person_id)
    return None