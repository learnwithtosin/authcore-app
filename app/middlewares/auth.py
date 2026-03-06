from fastapi import Depends, Request, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
from auth.jwt import verify_access_token
from models.user_model import User
import logging


logger = logging.getLogger(__name__)

# HttpBearer is responsible for extracting Bearer token from authorization headers
security = HTTPBearer()




class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials =await super().__call__(request)

        # Validate Credentials
        if credentials:
            print(credentials)
            if credentials.scheme != 'Bearer':
                raiseHttpException("Invalid authorization scheme. expected 'Bearer'")

            return self.verify_jwt(credentials.credentials, db)
            

        else:
            raiseHttpException("Invalid authorization code")

    def verify_jwt(self, token: str, db: Session):
        try:
            payload = verify_access_token(token)
            user_id = payload.get('sub')
            if user_id is None:
                return False

            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raiseHttpException("user does not exist")
            
            if not user.is_active:
                raiseHttpException("User account is deactivated")

            return user

        except Exception as e:
            raiseHttpException(f"JWT verification failed: {e}")

def raiseHttpException(e, status=status.HTTP_403_FORBIDDEN):
    raise HTTPException(
        status_code= status,
        detail= {
            "message": e,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

AuthMiddleware = JWTBearer()