from fastapi import FastAPI, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models.user_model import User
from schemas.auth import LoginRequest, LoginResponse
from auth.jwt import create_access_token
from fastapi.responses import RedirectResponse
from config.oauth import oauth
from datetime import datetime
from config.oauth import AUTH0_DOMAIN, AUTH0_CLIENT_ID
from fastapi import APIRouter
import logging
import bcrypt
import pymysql


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/oauth",
    tags=["Oauth"]
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    try:
        return await oauth.auth0.authorize_redirect(request, redirect_uri = redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auth Error: Failed to Authenticate User {e}"
        )

@router.get("/callback", name="callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.auth0.authorize_access_token(request)

        user_info = token.get("userinfo") or {}

        email = user_info.get("email")
        sub = user_info.get("sub")

        if not email or not sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auth Error: Required user info missing from provider"
            )

        user = db.query(User).filter(User.email == email).first()

        if not user:
            full_name = user_info.get("name", "")
            first_name, *rest = full_name.split(" ")
            last_name = " ".join(rest) if rest else None

            user = User(
                email=email,
                first_name=first_name or None,
                last_name=last_name,
                password_hash=None,          
                auth_provider="auth0",
                oauth_sub=sub,
                is_active=True,
                is_verified=True,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "user_id": str(user.id),
                "email": user.email,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": user.email,
            "id": user.id,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auth Error: Failed to generate token: {str(e)}"
        )


@router.get("/logout")
def logout(request: Request):
    return_url = "http://localhost:8000"

    logout_url = (
        f"https://{AUTH0_DOMAIN}/v2/logout?"
        f"client_id={AUTH0_CLIENT_ID}&"
        f"returnTo={return_url}"
    )

    return RedirectResponse(url = logout_url)