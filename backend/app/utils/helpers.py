"""
Helper utility functions
"""
import re
import random
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_otp(length: int = 6) -> str:
    """
    Generate random OTP code
    
    Args:
        length: Length of OTP code (default: 6)
        
    Returns:
        OTP code string
    """
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text
    
    Args:
        text: Text to convert to slug
        
    Returns:
        Slug string
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    
    # Remove all non-word characters except hyphens
    slug = re.sub(r'[^\w\-]+', '', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug


def generate_order_number() -> str:
    """
    Generate unique order number in format: ORD-YYYYMMDD-XXXX
    
    Returns:
        Order number string
    """
    date_str = datetime.now().strftime("%Y%m%d")
    # Generate 4-digit random number
    random_str = "".join([str(random.randint(0, 9)) for _ in range(4)])
    return f"ORD-{date_str}-{random_str}"


def normalize_phone_e164(phone: str) -> str:
    """
    Normalize phone to E.164 (e.g. 25137745414 -> +25137745414).
    Use for env/config values so they match DB (auth stores E.164).
    """
    if not phone or not isinstance(phone, str):
        return phone
    s = phone.strip()
    if s.startswith("+"):
        return s
    return f"+{s}"


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (basic validation)

    Args:
        phone: Phone number string

    Returns:
        True if valid format, False otherwise
    """
    # Basic E.164 format validation (starts with +, followed by digits)
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email string
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def calculate_delivery_dates(eta_min_days: int, eta_max_days: int) -> tuple:
    """
    Calculate expected delivery date range
    
    Args:
        eta_min_days: Minimum delivery days
        eta_max_days: Maximum delivery days
        
    Returns:
        Tuple of (from_date, to_date)
    """
    today = datetime.now().date()
    from_date = today + timedelta(days=eta_min_days)
    to_date = today + timedelta(days=eta_max_days)
    return (from_date, to_date)

