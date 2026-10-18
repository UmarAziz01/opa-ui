import json
import logging
import subprocess
import tempfile
import time
from typing import Any, Dict, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import ConflictException, EntityNotFoundException
from app.common.utils import current_epoch
from app.modules.organizations.models import Organization
from app.modules.policies.models import Permission, Role, TargetUserRoleMapping, role_permissions
from app.modules.policies.rego_generator import build_opa_data_json, generate_rego_policy
from app.modules.policies.schemas import (
    PermissionCreateRequest,
    PolicySimulationInput,
    RoleCreateRequest,
    RoleUpdateRequest,
    SubjectRoleAssignRequest,
)
from app.workers.bundle_compiler import compile_and_upload_bundle

logger = logging.getLogger(__name__)


# ── Permissions ───────────────────────────────────────────────────────────────

async def create_permission(
    db: AsyncSession,
    org_id: UUID,
    payload: PermissionCreateRequest,
) -> Permission:
    res = await db.execute(
        select(Permission.id).where(
            Permission.organization_id == org_id,
            Permission.resource == payload.resource,
            Permission.action == payload.action,
        )
    )
    if res.scalar_one_or_none():
        raise ConflictException(f"Permission '{payload.resource}:{payload.action}' sudah ada di organisasi ini.")

    perm = Permission(
        organization_id=org_id,
        resource=payload.resource,
        action=payload.action,
        description=payload.description,
    )
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


async def list_permissions(db: AsyncSession, org_id: UUID) -> List[Permission]:
    res = await db.execute(
        select(Permission).where(Permission.organization_id == org_id).order_by(Permission.resource, Permission.action)
    )
    return list(res.scalars().all())


# ── Roles ─────────────────────────────────────────────────────────────────────

async def create_role(
    db: AsyncSession,
    org_id: UUID,
    payload: RoleCreateRequest,
) -> Role:
    res = await db.execute(
        select(Role.id).where(Role.organization_id == org_id, Role.name == payload.name)
    )
    if res.scalar_one_or_none():
        raise ConflictException(f"Role '{payload.name}' sudah ada di organisasi ini.")

    role = Role(
        organization_id=org_id,
        name=payload.name,
        description=payload.description,
    )

    if payload.permission_ids:
        perm_res = await db.execute(
            select(Permission).where(
                Permission.id.in_(payload.permission_ids),
                Permission.organization_id == org_id,
            )
        )
        role.permissions = list(perm_res.scalars().all())

    db.add(role)
    await db.commit()

    # Muat ulang permissions untuk response schema
    res_loaded = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
    )
    return res_loaded.scalar_one()


async def list_roles(db: AsyncSession, org_id: UUID) -> List[Role]:
    res = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.organization_id == org_id).order_by(Role.created_at.desc())
    )
    return list(res.scalars().all())


async def update_role(
    db: AsyncSession,
    org_id: UUID,
    role_id: UUID,
    payload: RoleUpdateRequest,
) -> Role:
    res = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id, Role.organization_id == org_id)
    )
    role = res.scalar_one_or_none()
    if not role:
        raise EntityNotFoundException("Role", str(role_id))

    if payload.name is not None:
        role.name = payload.name
    if payload.description is not None:
        role.description = payload.description
    if payload.permission_ids is not None:
        perm_res = await db.execute(
            select(Permission).where(
                Permission.id.in_(payload.permission_ids),
                Permission.organization_id == org_id,
            )
        )
        role.permissions = list(perm_res.scalars().all())

    await db.commit()
    await db.refresh(role)
    return role


# ── Subject Role Mappings ─────────────────────────────────────────────────────

async def assign_subject_role(
    db: AsyncSession,
    org_id: UUID,
    payload: SubjectRoleAssignRequest,
) -> TargetUserRoleMapping:
    # Verifikasi role
    role_res = await db.execute(
        select(Role).where(Role.id == payload.role_id, Role.organization_id == org_id)
    )
    if not role_res.scalar_one_or_none():
        raise EntityNotFoundException("Role", str(payload.role_id))

    # Cek duplikasi mapping
    existing = await db.execute(
        select(TargetUserRoleMapping).where(
            TargetUserRoleMapping.organization_id == org_id,
            TargetUserRoleMapping.role_id == payload.role_id,
            TargetUserRoleMapping.subject_identifier == payload.subject_identifier,
        )
    )
    mapping = existing.scalar_one_or_none()
    if mapping:
        return mapping

    mapping = TargetUserRoleMapping(
        organization_id=org_id,
        role_id=payload.role_id,
        subject_identifier=payload.subject_identifier,
    )
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def list_subject_mappings(db: AsyncSession, org_id: UUID) -> List[TargetUserRoleMapping]:
    res = await db.execute(
        select(TargetUserRoleMapping).where(TargetUserRoleMapping.organization_id == org_id)
    )
    return list(res.scalars().all())


# ── OPA Simulation & Dry Run ──────────────────────────────────────────────────

async def simulate_policy_decision(
    db: AsyncSession,
    org_id: UUID,
    sim_input: PolicySimulationInput,
) -> Dict[str, Any]:
    # 1. Ambil data organisasi
    org_res = await db.execute(select(Organization).where(Organization.id == org_id))
    org = org_res.scalar_one_or_none()
    if not org:
        raise EntityNotFoundException("Organization", str(org_id))

    # 2. Ambil state DB aktif: Roles & Mappings
    roles_res = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.organization_id == org_id)
    )
    roles = list(roles_res.scalars().all())

    mappings_res = await db.execute(
        select(TargetUserRoleMapping).options(selectinload(TargetUserRoleMapping.role)).where(TargetUserRoleMapping.organization_id == org_id)
    )
    mappings = list(mappings_res.scalars().all())

    # 3. Bentuk Rego Policy & Data JSON
    rego_content = generate_rego_policy(org.slug)
    data_content = build_opa_data_json(roles, mappings)

    # 4. Eksekusi `opa eval` via OPA binary lokal
    query_pkg = f"data.org.{org.slug.replace('-', '_')}.authz.allow"
    input_payload = {
        "subject": sim_input.subject,
        "resource": sim_input.resource,
        "action": sim_input.action,
        "context": sim_input.context or {},
    }

    start_time = time.perf_counter()
    with tempfile.NamedTemporaryFile("w", suffix=".rego", delete=True) as rego_f, \
         tempfile.NamedTemporaryFile("w", suffix=".json", delete=True) as data_f, \
         tempfile.NamedTemporaryFile("w", suffix=".json", delete=True) as input_f:

        rego_f.write(rego_content)
        rego_f.flush()

        data_f.write(json.dumps(data_content))
        data_f.flush()

        input_f.write(json.dumps(input_payload))
        input_f.flush()

        cmd = [
            "opa", "eval",
            "--format=json",
            "-d", rego_f.name,
            "-d", data_f.name,
            "-i", input_f.name,
            query_pkg,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            duration_ms = (time.perf_counter() - start_time) * 1000

            if res.returncode != 0:
                logger.error("OPA dry-run eval error: %s", res.stderr)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OPA eval engine gagal: {res.stderr.strip()}",
                )

            opa_res = json.loads(res.stdout)
            # Struktur output: {"result": [{"expressions": [{"value": true/false}]}]}
            allow = False
            result_list = opa_res.get("result", [])
            if result_list and result_list[0].get("expressions"):
                allow = bool(result_list[0]["expressions"][0].get("value"))

            return {
                "allow": allow,
                "evaluated_at": current_epoch(),
                "execution_time_ms": round(duration_ms, 2),
                "rego_package": query_pkg,
                "details": {
                    "input": input_payload,
                    "matched_roles": data_content["user_roles"].get(sim_input.subject, []),
                },
            }
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Evaluasi OPA melebihi batas waktu 5 detik.",
            )


# ── Bundle Compilation Integration ────────────────────────────────────────────

async def compile_organization_bundle(
    db: AsyncSession,
    tenant_id: UUID,
    org_id: UUID,
    user_id: UUID,
    environment: str = "production",
) -> Any:
    """Memicu compiler bundle untuk membuat tar.gz dan mengunggahnya ke MinIO."""
    bundle_record = await compile_and_upload_bundle(
        db=db,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        environment=environment,
    )
    return bundle_record