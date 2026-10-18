from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_user, get_db_session
from app.modules.auth.models import User
from app.modules.governance.schemas import ApprovalRequestCreate, ApprovalResponse, ReviewAction
from app.modules.governance.service import create_approval_request, list_approvals, process_approval_review
from app.modules.tenants.dependencies import require_active_tenant_subscription
from app.modules.tenants.models import Tenant

router = APIRouter(
    prefix="/tenants/{tenant_id}/orgs/{org_id}/governance",
    tags=["Governance & Approvals"],
)


@router.post(
    "/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajukan bundle ke environment target dengan validasi Quality Gate otomatis",
)
async def submit_approval(
    tenant_id: UUID,
    org_id: UUID,
    payload: ApprovalRequestCreate,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await create_approval_request(db, tenant_id, org_id, current_user.id, payload)


@router.get(
    "/approvals",
    response_model=List[ApprovalResponse],
    status_code=status.HTTP_200_OK,
    summary="Daftar seluruh tiket persetujuan rilis bundle",
)
async def get_approvals(
    tenant_id: UUID,
    org_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(PENDING|APPROVED|REJECTED)$"),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await list_approvals(db, org_id, status_filter)


@router.post(
    "/approvals/{approval_id}/review",
    response_model=ApprovalResponse,
    status_code=status.HTTP_200_OK,
    summary="Review pengajuan rilis (APPROVE / REJECT) - ORG_ADMIN Only",
)
async def review_approval(
    tenant_id: UUID,
    org_id: UUID,
    approval_id: UUID,
    payload: ReviewAction,
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(require_active_tenant_subscription),
    db: AsyncSession = Depends(get_db_session),
):
    return await process_approval_review(db, tenant_id, org_id, approval_id, current_user.id, payload)