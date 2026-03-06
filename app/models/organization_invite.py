from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base
from models.enums import OrgRole

class OrganizationInvite(Base):
    __tablename__ = "organization_invites"

    id = Column(Integer, primary_key=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    email = Column(String(255), index=True, nullable=False)

    role = Column(Enum(OrgRole), default=OrgRole.member)

    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", backref="invites")
