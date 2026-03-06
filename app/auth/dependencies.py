
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt import verify_access_token
from models.user_model import User


bearer_scheme = HTTPBearer(auto_error=False)  

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Extracts the JWT token from the Authorization header, verifies it,
    and returns the user object from the database.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = credentials.credentials
    payload = verify_access_token(token)  

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user









