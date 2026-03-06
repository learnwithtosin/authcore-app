from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user

from models.user_model import User
from models.organizations import Organization
from models.memberships import OrganizationMembership
from models.enums import OrgRole, MembershipStatus

from schemas.organizations import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationMemberResponse,
)
from schemas.memberships import (
    UpdateMembershipStatusRequest,
    InviteMemberRequest,
    UpdateMembershipRoleRequest,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

# ======================================================
# Dependencies
# ======================================================

def require_active_membership(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationMembership:
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.status == MembershipStatus.active,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or access denied",
        )

    return membership


def require_org_admin(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationMembership:
    membership = require_active_membership(
        organization_id=organization_id,
        db=db,
        current_user=current_user,
    )

    if membership.role != OrgRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return membership

# ======================================================
# Organizations
# ======================================================

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Organization)
        .filter(
            Organization.owner_id == current_user.id,
            Organization.name == payload.name,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an organization with this name",
        )

    organization = Organization(
        name=payload.name,
        owner_id=current_user.id,
    )
    db.add(organization)
    db.flush()

    membership = OrganizationMembership(
        user_id=current_user.id,
        organization_id=organization.id,
        role=OrgRole.admin,
        status=MembershipStatus.active,
    )
    db.add(membership)

    db.commit()
    db.refresh(organization)

    return organization


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
def list_my_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Organization)
        .join(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.status == MembershipStatus.active,
        )
        .all()
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationDetailResponse,
)
def get_organization_details(
    organization_id: int,
    membership: OrganizationMembership = Depends(require_active_membership),
):
    org = membership.organization

    return OrganizationDetailResponse(
        id=org.id,
        name=org.name,
        owner_id=org.owner_id,
        created_at=org.created_at,
        role=membership.role,
    )


# Members


@router.get(
    "/{organization_id}/members",
    response_model=list[OrganizationMemberResponse],
)
def list_members(
    organization_id: int,
    db: Session = Depends(get_db),
    _: OrganizationMembership = Depends(require_active_membership),
):
    memberships = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.organization_id == organization_id)
        .all()
    )

    return [
        OrganizationMemberResponse(
            user_id=m.user_id,
            email=m.user.email,
            first_name=m.user.first_name,
            last_name=m.user.last_name,
            role=m.role,
            status=m.status,
            joined_at=m.joined_at,
            is_active=m.user.is_active
        )
        for m in memberships
    ]


@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def invite_member(
    organization_id: int,
    payload: InviteMemberRequest = Body(...),
    db: Session = Depends(get_db),
    _: OrganizationMembership = Depends(require_org_admin),
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == payload.user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member",
        )

    membership = OrganizationMembership(
        user_id=payload.user_id,
        organization_id=organization_id,
        role=OrgRole.member,
        status=MembershipStatus.active,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    return OrganizationMemberResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=membership.role,
        is_active=user.is_active,
        status=membership.status,
        joined_at=membership.joined_at,
    )


@router.patch(
    "/{organization_id}/members/{user_id}/status",
    response_model=OrganizationMemberResponse,
)
def update_member_status(
    organization_id: int,
    user_id: int,
    payload: UpdateMembershipStatusRequest = Body(...),
    db: Session = Depends(get_db),
    _: OrganizationMembership = Depends(require_org_admin),
):
    
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.user_id == user_id,
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.status = payload.status
    db.commit()
    db.refresh(membership)

    user = db.query(User).filter(User.id == membership.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return OrganizationMemberResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        role=membership.role,
        status=membership.status,
        joined_at=membership.joined_at,
    )


@router.patch(
    "/{organization_id}/members/{user_id}/role",
    response_model=OrganizationMemberResponse,
)
def update_member_role(
    organization_id: int,
    user_id: int,
    payload: UpdateMembershipRoleRequest = Body(...),
    db: Session = Depends(get_db),
    _: OrganizationMembership = Depends(require_org_admin),
):
    
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.user_id == user_id,
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.role = payload.role
    db.commit()
    db.refresh(membership)

    user = db.query(User).filter(User.id == membership.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return OrganizationMemberResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        role=membership.role,
        status=membership.status,
        joined_at=membership.joined_at,
    )



@router.delete(
    "/{organization_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    admin_membership: OrganizationMembership = Depends(require_org_admin),
):
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    if membership.user_id == membership.organization.owner_id:
        raise HTTPException(status_code=400, detail="Cannot remove owner")

    if membership.user_id == admin_membership.user_id:
        raise HTTPException(status_code=400, detail="Admins cannot remove themselves")

    db.delete(membership)
    db.commit()
