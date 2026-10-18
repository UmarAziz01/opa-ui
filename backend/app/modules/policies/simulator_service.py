import asyncio
import json
import logging
import os
import tempfile
import time
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organizations.models import Organization
from app.modules.tenants.models import Tenant
from app.workers.bundle_compiler import DEFAULT_AUTHZ_REGO, fetch_org_rbac_snapshot

logger = logging.getLogger(__name__)


async def run_opa_eval_subprocess(
    rego_code: str,
    data_json: Dict[str, Any],
    input_json: Dict[str, Any],
    query: str = "data.policies.authz.allow",
) -> tuple[Any, float]:
    """Mengeksekusi binary OPA di runtime secara async menggunakan stdin/temporary file."""
    start_time = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmpdir:
        policy_path = os.path.join(tmpdir, "policy.rego")
        data_path = os.path.join(tmpdir, "data.json")
        input_path = os.path.join(tmpdir, "input.json")

        # Tulis temporary files
        with open(policy_path, "w", encoding="utf-8") as f:
            f.write(rego_code)

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data_json, f)

        with open(input_path, "w", encoding="utf-8") as f:
            json.dump(input_json, f)

        # Jalankan CLI OPA eval
        cmd = [
            "opa",
            "eval",
            "--format=json",
            f"--data={policy_path}",
            f"--data={data_path}",
            f"--input={input_path}",
            query,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="replace")
                logger.error(f"OPA eval error (code {proc.returncode}): {err_msg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sintaks Rego atau data tidak valid: {err_msg.strip()}",
                )

            res_obj = json.loads(stdout.decode("utf-8"))
            # Format output opa eval: {"result": [{"expressions": [{"value": true, ...}]}]}
            raw_result = res_obj.get("result", [])
            evaluated_val = False
            if raw_result and "expressions" in raw_result[0]:
                exprs = raw_result[0]["expressions"]
                if exprs:
                    evaluated_val = exprs[0].get("value", False)

            return evaluated_val, duration_ms

        except FileNotFoundError:
            logger.error("Binary 'opa' tidak terdeteksi di PATH sistem host/container.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Engine evaluasi OPA CLI tidak terpasang di host server.",
            )


async def simulate_policy_dry_run(
    db: AsyncSession,
    org_id: str,
    input_payload: Dict[str, Any],
    custom_rego: Optional[str] = None,
) -> Dict[str, Any]:
    # 1. Validasi eksistensi organisasi dan tenant
    query = (
        select(Organization, Tenant)
        .join(Tenant, Organization.tenant_id == Tenant.id)
        .where(Organization.id == org_id)
    )
    result = await db.execute(query)
    record = result.first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan.",
        )

    org, tenant = record.Organization, record.Tenant

    # 2. Ambil snapshot data RBAC saat ini dari DB
    rbac_data = await fetch_org_rbac_snapshot(db, str(org.id))

    # 3. Bentuk struktur data.json OPA
    data_bundle = {
        "tenants": {
            tenant.slug: {
                "orgs": {
                    org.slug: rbac_data
                }
            }
        }
    }

    # 4. Sematkan otomatis tenant & org slug ke input payload jika belum didefinisikan
    normalized_input = dict(input_payload)
    normalized_input.setdefault("tenant", tenant.slug)
    normalized_input.setdefault("org", org.slug)

    # 5. Jalankan evaluasi
    rego_to_use = custom_rego if custom_rego and custom_rego.strip() else DEFAULT_AUTHZ_REGO
    is_allowed, latency = await run_opa_eval_subprocess(
        rego_code=rego_to_use,
        data_json=data_bundle,
        input_json=normalized_input,
        query="data.policies.authz.allow",
    )

    return {
        "allowed": bool(is_allowed),
        "evaluation_result": is_allowed,
        "execution_time_ms": latency,
        "simulated_at": datetime.now(timezone.utc).isoformat(),
        "details": f"Evaluasi berhasil pada scope: tenant '{tenant.slug}', org '{org.slug}'",
    }