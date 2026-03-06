from sqlalchemy import Integer, Column, String, DateTime, Enum, ForeignKey
from .base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship



class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    revoked_at = Column(DateTime, server_default=func.now())
