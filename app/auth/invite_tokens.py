import secrets
import hashlib
from datetime import datetime, timedelta

INVITE_EXPIRY_DAYS = 7

def generate_invite_token():
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=INVITE_EXPIRY_DAYS)

    return raw_token, token_hash, expires_at
