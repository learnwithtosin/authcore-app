from pydantic import BaseModel
from datetime import datetime
from models.enums import OrgRole, MembershipStatus


class OrganizationMemberResponse(BaseModel):
    user_id: int
    role: OrgRole
    status: MembershipStatus
    joined_at: datetime

    class Config:
        from_attributes = True


class UpdateMembershipStatusRequest(BaseModel):
    status: MembershipStatus


class InviteMemberRequest(BaseModel):
    user_id: int


class UpdateMembershipRoleRequest(BaseModel):
    role: OrgRole