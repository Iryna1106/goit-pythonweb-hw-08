from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repo_contacts
from src.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
def read_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    first_name: Optional[str] = Query(None, description="Фільтр за іменем (частковий збіг)"),
    last_name: Optional[str] = Query(None, description="Фільтр за прізвищем (частковий збіг)"),
    email: Optional[str] = Query(None, description="Фільтр за email (частковий збіг)"),
    db: Session = Depends(get_db),
):
    return repo_contacts.get_contacts(
        db, skip=skip, limit=limit, first_name=first_name, last_name=last_name, email=email
    )


@router.get("/upcoming-birthdays", response_model=List[ContactResponse])
def upcoming_birthdays(
    days: int = Query(7, ge=1, le=365, description="Кількість днів наперед"),
    db: Session = Depends(get_db),
):
    return repo_contacts.get_upcoming_birthdays(db, days=days)


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repo_contacts.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    if repo_contacts.get_contact_by_email(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists",
        )
    return repo_contacts.create_contact(db, body)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db)):
    if body.email:
        existing = repo_contacts.get_contact_by_email(db, body.email)
        if existing and existing.id != contact_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another contact with this email already exists",
            )
    contact = repo_contacts.update_contact(db, contact_id, body)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repo_contacts.delete_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
