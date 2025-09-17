"""
People CRUD operations.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from .. import models, schemas
from .common import _validate_unique_person

def get_people(db: Session, user_id: int, person_ids: list[int] | None = None) -> list[models.Person]:
    """Get all active people for a user, optionally filtered by person IDs."""
    query = db.query(models.Person).filter(
        models.Person.user_id == user_id,
        models.Person.active == True
    )
    if person_ids:
        query = query.filter(models.Person.id.in_(person_ids))
    return query.all()

def get_all_people(db: Session) -> list[models.Person]:
    """Get all active people regardless of user."""
    return db.query(models.Person).filter(models.Person.active == True).all()

def get_person(db: Session, user_id: int, person_id: int) -> models.Person | None:
    """Get a single active person by ID for a specific user."""
    return db.query(models.Person).filter(
        models.Person.id == person_id,
        models.Person.user_id == user_id,
        models.Person.active == True
    ).first()

def get_person_any_status(db: Session, person_id: int) -> models.Person | None:
    """Get a person by ID regardless of active status."""
    return db.query(models.Person).filter(models.Person.id == person_id).first()

def get_person_by_id(db: Session, person_id: int) -> models.Person | None:
    """Get an active person by ID regardless of user."""
    return db.query(models.Person).filter(
        models.Person.id == person_id,
        models.Person.active == True
    ).first()

def create_person(db: Session, person: schemas.PersonCreate) -> models.Person:
    """Create a new person."""
    # Validate unique name and is_me constraint
    _validate_unique_person(db=db, user_id=person.user_id, name=person.name, is_me=person.is_me)
    
    db_person = models.Person(
        name=person.name,
        user_id=person.user_id,
        is_me=person.is_me
    )
    db.add(db_person)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def update_person(db: Session, user_id: int, person_id: int, person: schemas.PersonUpdate) -> models.Person:
    """Update an existing person."""
    db_person = get_person(db=db, user_id=user_id, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Validate unique name and is_me constraint if being updated
    if person.name is not None or person.is_me is not None:
        name = person.name if person.name is not None else db_person.name
        is_me = person.is_me if person.is_me is not None else db_person.is_me
        _validate_unique_person(db=db, user_id=user_id, name=name, is_me=is_me, exclude_id=person_id)
    
    # Update fields
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def update_person_by_id(db: Session, person_id: int, person: schemas.PersonUpdate) -> models.Person:
    """Update a person by ID without requiring user_id in signature."""
    db_person = get_person_by_id(db=db, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Validate unique name and is_me constraint if being updated
    if person.name is not None or person.is_me is not None:
        name = person.name if person.name is not None else db_person.name
        is_me = person.is_me if person.is_me is not None else db_person.is_me
        _validate_unique_person(db=db, user_id=db_person.user_id, name=name, is_me=is_me, exclude_id=person_id)
    
    # Update fields
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Constraint violation: {e.orig}")
    db.refresh(db_person)
    return db_person

def deactivate_person(db: Session, user_id: int, person_id: int) -> models.Person:
    """Deactivate a person (soft delete)."""
    db_person = get_person(db=db, user_id=user_id, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    db_person.active = False
    db_person.deleted_at = datetime.now()
    db.commit()
    return db_person

def activate_person(db: Session, user_id: int, person_id: int) -> models.Person:
    """Activate a person."""
    db_person = get_person_any_status(db=db, person_id=person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    if db_person.active:
        raise HTTPException(status_code=404, detail="Person is already active")
    
    db_person.active = True
    db_person.deleted_at = None
    db.commit()
    return db_person
