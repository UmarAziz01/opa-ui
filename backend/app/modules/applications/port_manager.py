import socket
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.config import settings
from app.modules.applications.models import Application


def is_host_port_free(port: int) -> bool:
    """Cek langsung ke OS host apakah port TCP sedang digunakan."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return True
        except socket.error:
            return False


async def allocate_sidecar_port(
    db: AsyncSession,
    requested_port: Optional[int] = None,
    current_app_id: Optional[str] = None,
) -> int:
    """Mengalokasikan port sidecar di rentang 18100-18999 secara aman."""
    start_port = getattr(settings, "OPA_PORT_RANGE_START", 18100)
    end_port = getattr(settings, "OPA_PORT_RANGE_END", 18999)

    # 1. Jika User Meminta Port Khusus
    if requested_port is not None:
        if not (start_port <= requested_port <= end_port):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Port {requested_port} di luar range ({start_port}-{end_port}).",
            )

        query = select(Application.id).where(
            Application.sidecar_port == requested_port,
            Application.deleted_at.is_(None),
        )
        if current_app_id:
            query = query.where(Application.id != current_app_id)

        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Port {requested_port} sudah dicatat oleh aplikasi lain di database.",
            )

        if not is_host_port_free(requested_port):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Port {requested_port} sedang dipakai proses aktif lain di host OS.",
            )

        return requested_port

    # 2. Alokasi Otomatis (Sequential Scan)
    result = await db.execute(
        select(Application.sidecar_port).where(
            Application.sidecar_port.isnot(None),
            Application.deleted_at.is_(None),
        )
    )
    used_db_ports = set(result.scalars().all())

    for candidate_port in range(start_port, end_port + 1):
        if candidate_port not in used_db_ports:
            if is_host_port_free(candidate_port):
                return candidate_port

    raise HTTPException(
        status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
        detail="Semua port sidecar OPA di rentang yang dialokasikan sedang penuh.",
    )