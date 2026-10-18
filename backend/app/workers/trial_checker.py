import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.modules.tenants.models import Tenant

logger = logging.getLogger(__name__)


async def check_and_expire_trials() -> int:
    """Mengecek dan memperbarui status tenant yang masa trialnya habis."""
    now_utc = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as session:
        try:
            # Query tenant yang aktif trialing tapi sudah melewati batas waktu
            stmt = (
                update(Tenant)
                .where(
                    Tenant.subscription_status == "TRIALING",
                    Tenant.trial_ends_at <= now_utc,
                )
                .values(subscription_status="EXPIRED")
                .execution_options(synchronize_session=False)
            )
            result = await session.execute(stmt)
            await session.commit()
            expired_count = result.rowcount
            if expired_count > 0:
                logger.warning(
                    "Trial checker: %s tenant telah kedaluwarsa dan diubah ke EXPIRED.",
                    expired_count,
                )
            return expired_count
        except Exception as exc:
            await session.rollback()
            logger.error("Gagal menjalankan scheduled trial checker: %s", exc)
            return 0


async def start_trial_checker_loop(interval_seconds: int = 3600) -> None:
    """Background task loop yang berjalan secara berkala."""
    logger.info(
        "Memulai loop worker trial checker (interval: %s detik)...",
        interval_seconds,
    )
    while True:
        try:
            await check_and_expire_trials()
        except asyncio.CancelledError:
            logger.info("Worker trial checker dihentikan.")
            break
        except Exception as exc:
            logger.error("Error tak terduga pada loop trial checker: %s", exc)
        await asyncio.sleep(interval_seconds)