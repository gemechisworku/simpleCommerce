"""
Webhooks (e.g. Telegram bot updates for OTP delivery)
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.auth import OTPCode
from app.services.otp_delivery import send_otp_telegram

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Telegram Bot API webhook. When user opens the OTP link and taps Start,
    we receive /start otp_<token>, find the OTP, send the code to their chat, and clear the token.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "Bot not configured"}
    try:
        body = await request.json()
    except Exception as e:
        logger.warning("Telegram webhook invalid JSON: %s", e)
        return {"ok": False}
    msg = body.get("message") if isinstance(body, dict) else None
    if not msg or not isinstance(msg, dict):
        return {"ok": True}
    text = (msg.get("text") or "").strip()
    chat = msg.get("chat") if isinstance(msg.get("chat"), dict) else None
    chat_id = chat.get("id") if chat else None
    if not text.startswith("/start otp_") or chat_id is None:
        return {"ok": True}
    token = text.split(maxsplit=1)[1].strip() if len(text.split(maxsplit=1)) > 1 else ""
    if not token:
        return {"ok": True}
    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.delivery_token == token,
            OTPCode.used_at.is_(None),
            OTPCode.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    if not otp:
        logger.info("Telegram OTP link: token not found or expired")
        return {"ok": True}
    sent = send_otp_telegram(str(chat_id), otp.code)
    if sent:
        otp.delivery_token = None
        db.commit()
        logger.info("OTP sent via Telegram link to chat_id=%s for identifier=%s", chat_id, otp.identifier)
    return {"ok": True}
