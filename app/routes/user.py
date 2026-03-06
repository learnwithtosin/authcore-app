from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import logging
from database import get_db
from models.user_model import User
from models.refresh_tokens import RefreshToken
from datetime import datetime
from auth.jwt import create_access_token
from middlewares.auth import AuthMiddleware
from schemas.user import (
    UserResponse,
    UserCreateRequest,
    UserRegisterResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)



@router.post("/register", response_model=UserRegisterResponse, status_code=201)
def register_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash password using bcrypt
    hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create new user
    new_user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    access_token = create_access_token({"sub": str(new_user.id)})

    return UserRegisterResponse(user=new_user, access_token=access_token)



@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(AuthMiddleware)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthMiddleware)
):
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthMiddleware)
):
    
    if not bcrypt.checkpw(
        payload.current_password.encode(),
        current_user.password_hash.encode()  
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.password_hash = bcrypt.hashpw(
        payload.new_password.encode(),
        bcrypt.gensalt()
    ).decode()  

    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    ).update(
        {"is_revoked": True},
        synchronize_session=False
    )

    db.commit()

    return  



@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthMiddleware)
):
    current_user.is_active = False
    db.commit()
    return

