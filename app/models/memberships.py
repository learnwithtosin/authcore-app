from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base
from .enums import OrgRole, MembershipStatus



class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    role = Column(
        Enum(OrgRole),
        nullable=False,
        default=OrgRole.member,
    )

    status = Column(
        Enum(MembershipStatus),
        nullable=False,
        default=MembershipStatus.active,
    )

    joined_at = Column(DateTime, server_default=func.now())

    user = relationship(
        "User",
        back_populates="memberships",
    )

    organization = relationship(
        "Organization",
        back_populates="memberships",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_user_organization",
        ),
    )


