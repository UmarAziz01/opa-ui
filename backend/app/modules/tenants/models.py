import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    subscription_tier = Column(String(50), nullable=False, default="FREE_TRIAL")
    subscription_status = Column(String(50), nullable=False, default="TRIALING")
    trial_starts_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    trial_ends_at = Column(DateTime(timezone=True), server_default=text("now() + interval '30 days'"), nullable=False)
    
    max_organizations = Column(Integer, default=3, nullable=False)
    max_developers = Column(Integer, default=5, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_user_id])
    members = relationship("TenantMember", back_populates="tenant", cascade="all, delete-orphan")


class TenantMember(Base):
    __tablename__ = "tenant_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_role = Column(String(50), nullable=False, default="TENANT_MEMBER")  # TENANT_ADMIN | TENANT_MEMBER
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tenant = relationship("Tenant", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_members_tenant_user"),
    )