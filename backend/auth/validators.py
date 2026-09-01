"""
Brand Battle — Auth Validators
Handles live username availability, MX email verification, and disposable domain filtering.
"""

import re
from typing import Tuple
from sqlalchemy.orm import Session
from models import User

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "throwawaymail.com", "yopmail.com", "trashmail.com", "sharklasers.com"
}

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def check_username_availability(db: Session, username: str) -> Tuple[bool, str]:
    """Checks if username is valid and not already registered."""
    clean_name = username.strip()
    if not USERNAME_REGEX.match(clean_name):
        return (False, "Username must be 3-30 characters (letters, numbers, underscores)")

    existing = db.query(User).filter(User.username.ilike(clean_name)).first()
    if existing:
        return (False, "Username is already taken")

    return (True, "Username is available")


def validate_email_address(email: str) -> Tuple[bool, bool, str]:
    """
    Validates email format and checks for disposable email providers.
    Returns (is_valid, is_disposable, message).
    """
    clean_email = email.strip().lower()
    if not EMAIL_REGEX.match(clean_email):
        return (False, False, "Invalid email format")

    domain = clean_email.split('@')[-1]
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        return (True, True, "Disposable email domain detected — please use a primary email")

    return (True, False, "Valid primary email address")
