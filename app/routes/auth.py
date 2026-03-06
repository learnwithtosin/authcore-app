from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
import hashlib

from database import get_db
from models.user_model import User
from models.refresh_tokens import RefreshToken
from schemas.auth import LoginRequest, LoginResponse, ResetPasswordRequest

from auth.jwt import (
    create_access_token,
    create_refresh_token,
    hash_token,
    get_refresh_token_expiry
)

from auth.password_reset import (
    generate_reset_token,
    revoke_all_user_refresh_tokens
)
from models.password_reset import PasswordResetToken

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if user.auth_provider != "local":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses OAuth login. Please continue with Google."
        )


    if not user or not bcrypt.checkpw(
        payload.password.encode(),
        user.password_hash.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        claims={"sub": str(user.id), "email": user.email}
    )

    refresh_token = create_refresh_token()
    refresh_token_hash = hash_token(refresh_token)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=get_refresh_token_expiry()
        )
    )
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/refresh", response_model=LoginResponse)
def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    token_hash = hash_token(refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # rotate old token
    db_token.is_revoked = True

    new_refresh = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=db_token.user_id,
            token_hash=hash_token(new_refresh),
            expires_at=get_refresh_token_expiry()
        )
    )

    db.commit()

    new_access = create_access_token(
        claims={"sub": str(db_token.user_id)}
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.is_active:
        return {"message": "If the email exists, a reset link has been sent."}

    raw_token, token_hash, expires_at = generate_reset_token()

    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
    )
    db.commit()

    # TODO: send email
    print(f"Password reset token: {raw_token}")

    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()

    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used.is_(False),
            PasswordResetToken.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user = reset_token.user

    user.password_hash = bcrypt.hashpw(
        payload.new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    reset_token.used = True

    # 🔐 revoke all refresh tokens on password change
    revoke_all_user_refresh_tokens(user.id, db)

    db.commit()

    return {"message": "Password reset successful"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    token_hash = hash_token(refresh_token)

    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False)
        )
        .first()
    )

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return
