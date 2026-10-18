import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PolicyBundle(Base):
    __tablename__ = "policy_bundles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, index=True)
    version = Column(Integer, nullable=False, default=1)

    # Deployment target & GitOps
    environment = Column(String(30), nullable=False, default="staging")  # 'staging' | 'production'
    git_commit = Column(String(40), nullable=True)
    file_diff = Column(Text, nullable=True)
    bundle_size_bytes = Column(BigInteger, default=0)

    # Quality Gate (opa test)
    test_passed = Column(Boolean, default=False)
    test_output = Column(Text, nullable=True)

    # S3 / MinIO Metadata
    s3_bucket = Column(String(100), nullable=False, default="opa-bundles")
    s3_object_key = Column(String(255), nullable=True)
    checksum_sha256 = Column(String(64), nullable=True)
    status = Column(String(30), default="DRAFT", nullable=False)  # DRAFT, BUILDING, ACTIVE, ARCHIVED, REVOKED

    # Audit & Diff Helpers
    change_summary = Column(String(255), nullable=True)
    snapshot_data = Column(JSONB, nullable=True)
    parent_bundle_id = Column(UUID(as_uuid=True), ForeignKey("policy_bundles.id", ondelete="SET NULL"), nullable=True)

    compiled_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", foreign_keys=[tenant_id])
    organization = relationship("Organization", foreign_keys=[organization_id])
    application = relationship("Application", foreign_keys=[application_id])
    compiler = relationship("User", foreign_keys=[compiled_by])
    parent_bundle = relationship("PolicyBundle", remote_side=[id])

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "organization_id",
            "application_id",
            "environment",
            "version",
            name="uq_policy_bundles_version_scope",
        ),
    )