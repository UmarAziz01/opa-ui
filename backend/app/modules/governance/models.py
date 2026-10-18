import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class BundleApproval(Base):
    __tablename__ = "bundle_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    bundle_id = Column(UUID(as_uuid=True), ForeignKey("policy_bundles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    
    target_environment = Column(String(30), nullable=False, default="production")
    status = Column(String(30), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED, CANCELLED
    
    # Quality Gate (opa test)
    tests_passed = Column(Boolean, default=False, nullable=False)
    test_output = Column(Text, nullable=True)
    
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    bundle = relationship("PolicyBundle")
    requester = relationship("User", foreign_keys=[requester_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])