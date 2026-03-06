import secrets
import hashlib
from datetime import datetime, timedelta

REFRESH_TOKEN_EXPIRE_DAYS = 14

def create_refresh_token():
    token = secrets.token_urlsafe(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash

def refresh_token_expiry():
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
