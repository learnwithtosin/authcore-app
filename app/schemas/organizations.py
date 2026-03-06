from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from models.enums import OrgRole
from typing import Optional



class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrganizationDetailResponse(OrganizationResponse):
    role: OrgRole

class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: OrgRole = OrgRole.member

class AcceptInviteRequest(BaseModel):
    token: str


class OrganizationMemberResponse(BaseModel):
    user_id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    role: str
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True

class AcceptInviteRequest(BaseModel):
    token: str = Field(..., min_length=10)