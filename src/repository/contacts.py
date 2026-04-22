from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import extract, or_, select
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas.contacts import ContactCreate, ContactUpdate


def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
) -> List[Contact]:
    stmt = select(Contact)
    if first_name:
        stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
    stmt = stmt.order_by(Contact.id).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    return db.get(Contact, contact_id)


def get_contact_by_email(db: Session, email: str) -> Optional[Contact]:
    stmt = select(Contact).where(Contact.email == email)
    return db.execute(stmt).scalar_one_or_none()


def create_contact(db: Session, body: ContactCreate) -> Contact:
    contact = Contact(**body.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(db: Session, contact_id: int, body: ContactUpdate) -> Optional[Contact]:
    contact = db.get(Contact, contact_id)
    if contact is None:
        return None
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int) -> Optional[Contact]:
    contact = db.get(Contact, contact_id)
    if contact is None:
        return None
    db.delete(contact)
    db.commit()
    return contact


def get_upcoming_birthdays(db: Session, days: int = 7) -> List[Contact]:
    """Return contacts whose birthday (ignoring year) falls within the next `days` days,
    starting from today (inclusive).

    Handles year boundary (e.g. today=Dec 28, window crosses into January).
    """
    today = date.today()
    end = today + timedelta(days=days)

    today_md = (today.month, today.day)
    end_md = (end.month, end.day)

    def month_day_tuple(d: date) -> tuple[int, int]:
        return (d.month, d.day)

    # Build SQL condition based on (month, day) without year.
    # If the window does not cross year boundary: today_md <= bd_md <= end_md.
    # Otherwise we split the window into two ranges.
    month = extract("month", Contact.birthday)
    day = extract("day", Contact.birthday)

    if today_md <= end_md:
        condition = or_(
            (month > today_md[0]) & (month < end_md[0]),
            (month == today_md[0]) & (day >= today_md[1]) & (month < end_md[0]),
            (month == end_md[0]) & (day <= end_md[1]) & (month > today_md[0]),
            (month == today_md[0]) & (month == end_md[0]) & (day >= today_md[1]) & (day <= end_md[1]),
        )
    else:
        # window wraps around year end
        condition = or_(
            (month > today_md[0]),
            (month == today_md[0]) & (day >= today_md[1]),
            (month < end_md[0]),
            (month == end_md[0]) & (day <= end_md[1]),
        )

    stmt = select(Contact).where(condition).order_by(month, day)
    contacts = list(db.execute(stmt).scalars().all())

    # Final refinement in Python to guarantee exact semantics across edge cases.
    def in_window(bd: date) -> bool:
        bd_md = (bd.month, bd.day)
        if today_md <= end_md:
            return today_md <= bd_md <= end_md
        return bd_md >= today_md or bd_md <= end_md

    return [c for c in contacts if in_window(c.birthday)]
