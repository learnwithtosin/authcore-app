import secrets
import hashlib
from sqlalchemy.orm import Session
from models.refresh_tokens import RefreshToken
from datetime import datetime, timedelta

RESET_TOKEN_EXP_MINUTES = 15

def generate_reset_token() -> tuple[str, str, datetime]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXP_MINUTES)

    return raw_token, token_hash, expires_at


def revoke_all_user_refresh_tokens(user_id: int, db: Session) -> None:
    """
    Revoke all active refresh tokens for a user.
    Used on password change, password reset, or security events.
    """
    (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.utcnow()
        )
        .update(
            {"is_revoked": True},
            synchronize_session=False
        )
    )
