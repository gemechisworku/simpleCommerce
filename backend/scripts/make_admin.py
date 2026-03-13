"""
One-off script: make a user with the given phone an admin (or create them as admin).
Usage: python -m scripts.make_admin [phone]
  e.g. python -m scripts.make_admin +251937745414
If no phone given, uses MAKE_ADMIN_PHONE env var.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.helpers import normalize_phone_e164


def main():
    raw = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MAKE_ADMIN_PHONE", "")).strip()
    phone = normalize_phone_e164(raw) if raw else ""
    if not phone:
        print("Usage: python -m scripts.make_admin +251937745414")
        sys.exit(1)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            if user.role == UserRole.ADMIN:
                print(f"User {phone} is already admin.")
                return
            user.role = UserRole.ADMIN
            db.commit()
            print(f"Updated {phone} to admin.")
        else:
            user = User(
                phone=phone,
                phone_verified=True,
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"Created admin user: {phone}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
