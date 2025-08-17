from fastapi import APIRouter, Depends
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
    return crud.get_people(db)

# Get a person
@router.get("/{person_id}", response_model=schemas.PersonOut)
def get_person(person_id: int, db: Session = Depends(get_db)):
    return crud.get_person(db, person_id)

# Update a person
@router.patch("/{person_id}", response_model=schemas.PersonOut)
def update_person(person_id: int, person: schemas.PersonUpdate, db: Session = Depends(get_db)):
    return crud.update_person(db, person_id, person)

# Delete a person
@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    crud.delete_person(db, person_id)
    return