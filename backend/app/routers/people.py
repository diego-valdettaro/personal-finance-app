from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/people", tags=["people"])

# Create a person
@router.post("/", response_model=schemas.PersonOut, status_code=201)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    return crud.create_person(db, person)
    
# List all people
@router.get("/", response_model=list[schemas.PersonOut])
def get_people(db: Session = Depends(get_db)):
    return crud.get_all_people(db)

# Get a person
@router.get("/{person_id}", response_model=schemas.PersonOut)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

# Update a person
@router.patch("/{person_id}", response_model=schemas.PersonOut)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    return crud.update_person_by_id(db, person_id, person)

# Deactivate a person
@router.patch("/{person_id}/deactivate", status_code=204)
def deactivate_person(person_id: int, db: Session = Depends(get_db)):
    # Note: We need to get user_id from the person record since people router doesn't have auth
    person = crud.get_person_any_status(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    crud.deactivate_person(db, person.user_id, person_id)
    return None

# Activate a person
@router.patch("/{person_id}/activate", status_code=204)
def activate_person(person_id: int, db: Session = Depends(get_db)):
    # Note: We need to get user_id from the person record since people router doesn't have auth
    person = crud.get_person_any_status(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    crud.activate_person(db, person.user_id, person_id)
    return None