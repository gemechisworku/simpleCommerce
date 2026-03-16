"""
One-off script: make a user admin by phone or Telegram ID.
Usage:
  python -m scripts.make_admin +251937745414   # by phone (E.164 or 251...)
  python -m scripts.make_admin 123456789        # by Telegram user ID (digits only)
Env: MAKE_ADMIN_PHONE or MAKE_ADMIN_TELEGRAM_ID if no arg.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.helpers import normalize_phone_e164


def main():
    raw = (sys.argv[1] if len(sys.argv) > 1 else None)
    if not raw:
        raw = os.environ.get("MAKE_ADMIN_PHONE") or os.environ.get("MAKE_ADMIN_TELEGRAM_ID") or ""
    raw = raw.strip()
    if not raw:
        print("Usage: python -m scripts.make_admin +251937745414  OR  python -m scripts.make_admin <telegram_user_id>")
        sys.exit(1)
    db = SessionLocal()
    try:
        # Treat as Telegram ID if it's all digits (no +)
        is_telegram_id = raw.isdigit()
        if is_telegram_id:
            user = db.query(User).filter(User.telegram_user_id == raw).first()
            if user:
                if user.role == UserRole.ADMIN:
                    print(f"User (Telegram {raw}) is already admin.")
                    return
                user.role = UserRole.ADMIN
                db.commit()
                print(f"Updated user (Telegram {raw}) to admin.")
            else:
                print(f"No user found with telegram_user_id={raw}. Log in via Telegram Mini App first, then run this again.")
        else:
            phone = normalize_phone_e164(raw)
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
