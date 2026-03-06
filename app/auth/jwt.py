from jose import jwt, JWTError
import os
import bcrypt
import hashlib
import secrets
from typing import Optional
from datetime import timedelta, datetime

# JWT CONFIG

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dd876043d55eebc302f01b3deeb99d8e5c3dceaf92675427c11067963fdefc55"
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_TIME", 20)
)

REFRESH_TOKEN_EXPIRATION_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", 7)
)


# ACCESS TOKENS

def create_access_token(
    claims: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    try:
        expiration_time = (
            datetime.utcnow() + expires_delta
            if expires_delta
            else datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES)
        )

        payload = claims.copy()
        payload.update({
            "exp": expiration_time,
            "type": "access"
        })

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except JWTError as e:
        raise e


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    except JWTError as e:
        raise e


# REFRESH TOKENS

def create_refresh_token() -> str:
    """
    Generates a secure random refresh token (NOT a JWT)
    """
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()



def verify_refresh_token(
    plain_token: str,
    hashed_token: str
) -> bool:
    """
    Compare refresh token with hashed version in DB
    """
    return bcrypt.checkpw(
        plain_token.encode(),
        hashed_token.encode()
    )


def get_refresh_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)








# OLD ONE

# from jose import jwt, JWTError
# import bcrypt
# import os
# from typing import Optional
# from datetime import timedelta, datetime

# SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dd876043d55eebc302f01b3deeb99d8e5c3dceaf92675427c11067963fdefc55')
# ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
# ACCESS_TOKEN_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_TIME', 5))



# def create_access_token(claims: dict, expires_delta: Optional[timedelta] = None)-> str:
#     try:
#         if expires_delta:
#             expiration_time = datetime.utcnow() + expires_delta
#         else:
#             expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTES)

#         claims.update({'exp': expiration_time})

#         return jwt.encode(claims, SECRET_KEY, ALGORITHM)
#     except JWTError as e:
#         raise e

# def verify_access_token(token: str):
#         try:
#             return jwt.decode(token, SECRET_KEY, ALGORITHM)
#         except JWTError as e:
#             raise e


