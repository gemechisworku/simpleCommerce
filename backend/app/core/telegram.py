"""
Telegram Web App initData validation.
See: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hmac
import hashlib
import urllib.parse
import json
from typing import Optional
from app.core.config import settings


def validate_telegram_init_data(init_data: str) -> Optional[dict]:
    """
    Validate Telegram WebApp initData and return parsed user if valid.

    Algorithm:
    - secret_key = HMAC-SHA256(key="WebAppData", message=bot_token)
    - data_check_string = sorted key=value (excluding hash) joined by newline
    - computed_hash = HMAC-SHA256(key=secret_key, message=data_check_string)
    - Valid if computed_hash == received hash and auth_date is not too old.

    Returns:
        Parsed dict with "user" (dict with id, first_name, last_name, username), "auth_date" (int)
        or None if invalid/missing token.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not init_data or not init_data.strip():
        return None

    try:
        params = urllib.parse.parse_qsl(init_data.strip())
        param_dict = dict(params)
        received_hash = param_dict.get("hash")
        if not received_hash:
            return None

        # Build data-check string: all pairs except hash, sorted by key
        data_check_string = "\n".join(
            k + "=" + v for k, v in sorted(param_dict.items(), key=lambda x: x[0]) if k != "hash"
        )

        # Secret key = HMAC-SHA256("WebAppData", bot_token)
        secret_key = hmac.new(
            b"WebAppData",
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Computed hash = HMAC-SHA256(secret_key, data_check_string)
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(computed_hash, received_hash):
            return None

        # Check auth_date age
        auth_date = int(param_dict.get("auth_date", 0))
        import time
        if abs(time.time() - auth_date) > settings.TELEGRAM_INIT_DATA_MAX_AGE_SECONDS:
            return None

        # Parse user (URL-encoded JSON)
        user_str = param_dict.get("user")
        if not user_str:
            return None
        user = json.loads(urllib.parse.unquote(user_str))

        return {"user": user, "auth_date": auth_date}
    except (json.JSONDecodeError, ValueError, KeyError):
        return None
