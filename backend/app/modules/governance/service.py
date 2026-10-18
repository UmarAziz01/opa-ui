import json
import logging
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, EntityNotFoundException, PermissionDeniedException
from app.modules.bundles.models import PolicyBundle
from app.modules.governance.models import BundleApproval
from app.modules.governance.schemas import ApprovalRequestCreate, ReviewAction
from app.modules.organizations.models import Organization, OrganizationMember
from app.modules.policies.rego_generator import build_opa_data_json, generate_rego_policy
from app.modules.policies.service import list_roles, list_subject_mappings
from app.workers.bundle_compiler import upload_bundle_stream, create_in_memory_bundle_tar_gz
import io

logger = logging.getLogger(__name__)


def run_opa_test_runner(
    rego_policy: str,
    data_json: dict,
    test_rego: Optional[str] = None,
) -> Tuple[bool, str]:
    """Menjalankan binary 'opa test' CLI pada temporary folder."""
    if not test_rego:
        # Default assertion test suite
        test_rego = """package policies.authz_test
import rego.v1
import data.policies.authz

test_default_deny if {
    not authz.allow with input as {"subject": "anonymous", "resource": "none", "action": "read"}
}
"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        policy_path = f"{tmp_dir}/policy.rego"
        data_path = f"{tmp_dir}/data.json"
        test_path = f"{tmp_dir}/policy_test.rego"

        with open(policy_path, "w") as f:
            f.write(rego_policy)
        with open(data_path, "w") as f:
            json.dump(data_json, f)
        with open(test_path, "w") as f:
            f.write(test_rego)

        cmd = ["opa", "test", tmp_dir, "-v", "--format=json"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = res.stdout if res.stdout else res.stderr
            return (res.returncode == 0), output
        except subprocess.TimeoutExpired:
            return False, "Error: Eksekusi 'opa test' melebihi timeout 10 detik."
        except Exception as exc:
            return False, f"Subprocess error: {str(exc)}"


async def create_approval_request(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    user_id: UUID,
    payload: ApprovalRequestCreate,
) -> BundleApproval:
    # 1. Validasi bundle
    bundle_res = await db.execute(
        select(PolicyBundle).where(
            PolicyBundle.id == payload.bundle_id,
            PolicyBundle.organization_id == org_id,
        )
    )
    bundle = bundle_res.scalar_one_or_none()
    if not bundle:
        raise EntityNotFoundException("PolicyBundle", str(payload.bundle_id))

    # 2. Ambil data RBAC dan struktur policy untuk Quality Gate
    org_res = await db.execute(select(Organization).where(Organization.id == org_id))
    org = org_res.scalar_one()

    roles = await list_roles(db, org_id)
    mappings = await list_subject_mappings(db, org_id)
    rego_code = generate_rego_policy(org.slug)
    data_dict = build_opa_data_json(roles, mappings)

    # 3. Jalankan Quality Gate (opa test)
    passed, test_log = run_opa_test_runner(
        rego_policy=rego_code,
        data_json=data_dict,
        test_rego=payload.test_suite_rego,
    )

    approval = BundleApproval(
        tenant_id=tenant_id,
        organization_id=org_id,
        bundle_id=bundle.id,
        requester_id=user_id,
        target_environment=payload.target_environment,
        status="PENDING" if passed else "REJECTED",
        tests_passed=passed,
        test_output=test_log,
        review_notes="Otomatis ditolak: Quality Gate (opa test) gagal." if not passed else None,
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval


async def process_approval_review(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    approval_id: UUID,
    reviewer_id: UUID,
    payload: ReviewAction,
) -> BundleApproval:
    # 1. Validasi hak akses reviewer (hanya ORG_ADMIN yang berhak)
    mem_res = await db.execute(
        select(OrganizationMember.org_role).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == reviewer_id,
        )
    )
    user_role = mem_res.scalar_one_or_none()
    if user_role != "ORG_ADMIN":
        raise PermissionDeniedException("Hanya anggota dengan role ORG_ADMIN yang berhak melakukan review approval.")

    # 2. Ambil record approval
    appr_res = await db.execute(
        select(BundleApproval).where(
            BundleApproval.id == approval_id,
            BundleApproval.organization_id == org_id,
        )
    )
    approval = appr_res.scalar_one_or_none()
    if not approval:
        raise EntityNotFoundException("BundleApproval", str(approval_id))

    if approval.status != "PENDING":
        raise ConflictException(f"Permintaan persetujuan ini sudah diproses dengan status '{approval.status}'.")

    # Cegah self-approval
    if approval.requester_id == reviewer_id:
        raise PermissionDeniedException("Requester tidak diizinkan menyetujui pengajuannya sendiri (Four-Eyes Principle).")

    approval.reviewer_id = reviewer_id
    approval.review_notes = payload.review_notes
    approval.reviewed_at = datetime.now(timezone.utc)

    if payload.action == "APPROVE":
        if not approval.tests_passed:
            raise ConflictException("Tidak dapat menyetujui bundle yang gagal melewati Quality Gate.")
        
        approval.status = "APPROVED"

        # Update environment bundle & sinkronkan current.tar.gz ke environment target
        bundle_res = await db.execute(select(PolicyBundle).where(PolicyBundle.id == approval.bundle_id))
        bundle = bundle_res.scalar_one()
        bundle.environment = approval.target_environment

        org_res = await db.execute(select(Organization).where(Organization.id == org_id))
        org = org_res.scalar_one()

        if bundle.snapshot_data:
            tar_stream, _, size_bytes = create_in_memory_bundle_tar_gz(
                tenant_slug=org.tenant_id.hex,
                org_slug=org.slug,
                version=bundle.version,
                rbac_data=bundle.snapshot_data,
            )
            # Timpa pointer current.tar.gz di environment target
            target_key = f"bundles/tenants/{org.tenant_id.hex}/orgs/{org.slug}/{approval.target_environment}/current.tar.gz"
            await upload_bundle_stream(object_key=target_key, data=tar_stream, length=size_bytes)
    else:
        approval.status = "REJECTED"

    await db.commit()
    await db.refresh(approval)
    return approval


async def list_approvals(
    db: AsyncSession,
    org_id: UUID,
    status_filter: Optional[str] = None,
) -> List[BundleApproval]:
    query = select(BundleApproval).where(BundleApproval.organization_id == org_id).order_by(BundleApproval.created_at.desc())
    if status_filter:
        query = query.where(BundleApproval.status == status_filter)
    res = await db.execute(query)
    return list(res.scalars().all())