"""
Pluggable OTP delivery (SMS / Telegram / email).
- Telegram: set TELEGRAM_BOT_TOKEN; pass telegram_user_id when requesting OTP (e.g. from Mini App init_data).
- SMS: set OTP_SMS_PROVIDER=twilio and Twilio env vars.
"""
import logging
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_otp_telegram(telegram_user_id: str, code: str) -> bool:
    """
    Send OTP to a Telegram user via the bot (private chat).
    telegram_user_id is the numeric Telegram user id (same as chat_id for private chats).
    Returns True if sent successfully.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not telegram_user_id or not telegram_user_id.strip():
        logger.warning("Telegram OTP not sent: TELEGRAM_BOT_TOKEN or telegram_user_id missing")
        return False

    chat_id = telegram_user_id.strip()
    text = f"Your verification code is: {code}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes."
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                url,
                json={"chat_id": chat_id, "text": text},
            )
        if r.status_code != 200:
            body = r.text
            logger.warning("Telegram sendMessage failed: status=%s body=%s", r.status_code, body)
            return False
        logger.info("OTP sent via Telegram to chat_id=%s", chat_id)
        return True
    except Exception as e:
        logger.exception("Telegram OTP send failed: %s", e)
        return False


def is_sms_configured() -> bool:
    """Return True if an SMS provider is configured and has credentials (so we can send to first-time users)."""
    provider = (settings.OTP_SMS_PROVIDER or "").strip().lower()
    if not provider or provider == "log":
        return False
    if provider == "twilio":
        return bool(
            settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER
        )
    return False


def send_otp_sms(phone: str, code: str) -> bool:
    """
    Send OTP code via SMS using the configured provider.
    Returns True if sent successfully, False otherwise (e.g. provider not configured).
    """
    provider = (settings.OTP_SMS_PROVIDER or "").strip().lower()
    if not provider or provider == "log":
        logger.info("OTP SMS not sent: no provider configured (set OTP_SMS_PROVIDER=twilio and Twilio env vars)")
        return False

    if provider == "twilio":
        return _send_otp_twilio(phone, code)

    logger.warning("Unknown OTP_SMS_PROVIDER=%s; OTP not sent", settings.OTP_SMS_PROVIDER)
    return False


def _send_otp_twilio(phone: str, code: str) -> bool:
    """Send OTP via Twilio API. Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER."""
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
        logger.warning("Twilio not configured: set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER")
        return False

    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your verification code is: {code}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.",
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone,
        )
        logger.info("OTP sent via Twilio to %s (sid=%s)", phone, message.sid)
        return True
    except Exception as e:  # twilio base exception or network
        logger.exception("Twilio SMS failed for %s: %s", phone, e)
        return False


def send_otp_email(email: str, code: str) -> bool:
    """
    Send OTP code via email. Not implemented; placeholder for future email provider.
    Returns False until an email provider is integrated.
    """
    logger.info("OTP for email %s (not sent in current implementation)", email)
    return False
