from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# Response for a user
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Request to update user profile
class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

# Request to change password
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# Request to create/register a user
class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Response for registration (user + access token)
class UserRegisterResponse(BaseModel):
    user: UserResponse
    access_token: str

