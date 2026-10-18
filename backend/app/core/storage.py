"""MinIO / S3-compatible storage wrapper untuk OPA Bundle Artifacts."""

from __future__ import annotations

import io
import logging
import asyncio
import time as _time
from datetime import timedelta
from typing import AsyncIterator, Optional, Tuple, Any

from minio import Minio
from minio.error import S3Error

from app.core.config import settings

logger = logging.getLogger(__name__)


class MinioUnavailable(Exception):
    """Diterjemahkan oleh exception handler menjadi status HTTP 503."""


def _resolve_endpoint() -> tuple[str, bool]:
    endpoint = settings.MINIO_ENDPOINT.strip()
    for prefix in ("http://", "https://"):
        if endpoint.startswith(prefix):
            endpoint = endpoint[len(prefix):]
    return endpoint.rstrip("/"), settings.MINIO_SECURE


_client: Optional[Minio] = None


def _get_client() -> Minio:
    global _client
    if _client is None:
        endpoint, secure = _resolve_endpoint()
        _client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=secure,
            region=settings.MINIO_REGION,
        )
    return _client


_skip_until: float = 0.0


def _swap_endpoint_for_public(url: str) -> str:
    public = settings.minio_public_endpoint.strip()
    if not public:
        return url
    internal = settings.MINIO_ENDPOINT.strip()
    if internal.startswith(("http://", "https://")):
        internal = internal.split("://", 1)[1].rstrip("/")
    public = public.rstrip("/")
    if public.startswith(("http://", "https://")):
        public = public.split("://", 1)[1]
    return url.replace(internal, public, 1)


async def _run_sync(func, *args, **kwargs):
    import asyncio
    return await asyncio.to_thread(func, *args, **kwargs)


async def ensure_bucket() -> None:
    """Membuat bucket utama saat startup jika belum tersedia."""
    if not settings.MINIO_ENABLED:
        return
    global _skip_until
    if _time.time() < _skip_until:
        return

    bucket_name = str(
        getattr(settings, "target_bucket", None)
        or getattr(settings, "MINIO_BUCKET_NAME", None)
        or getattr(settings, "MINIO_BUCKET", None)
        or "opa-bundles-staging"
    ).strip()

    def _do() -> None:
        client = _get_client()
        # bucket_exists(bucket_name: str)
        exists = client.bucket_exists(bucket_name)
        if not exists:
            client.make_bucket(bucket_name)
            logger.info("Bucket MinIO '%s' dibuat", bucket_name)
        else:
            logger.info("Bucket MinIO '%s' sudah tersedia", bucket_name)

    try:
        await _run_sync(_do)
        _skip_until = 0.0
    except S3Error as exc:
        _skip_until = _time.time() + 60.0
        logger.warning("MinIO unreachable saat ensure_bucket (%s). Cooldown 60s.", exc)
    except Exception as exc:
        _skip_until = _time.time() + 60.0
        logger.warning("Gagal ensure_bucket: %s. Cooldown 60s.", type(exc).__name__)


def build_bundle_key(
    tenant_slug: str,
    org_slug: str,
    environment: str,
    version: int,
) -> str:
    """Menyusun format path object standar MinIO untuk artefak tar.gz bundle."""
    return f"tenants/{tenant_slug}/orgs/{org_slug}/{environment}/bundle_v{version}.tar.gz"


async def upload_bundle_stream(
    object_key: str,
    data: io.BytesIO,
    length: int,
) -> None:
    if not settings.MINIO_ENABLED:
        raise MinioUnavailable("MinIO dinonaktifkan di environment ini")

    def _do() -> None:
        data.seek(0)
        _get_client().put_object(
            settings.MINIO_BUCKET,
            object_key,
            data,
            length=length,
            content_type="application/gzip",
        )

    try:
        await _run_sync(_do)
    except S3Error as exc:
        raise MinioUnavailable(f"Upload bundle MinIO gagal: {exc}") from exc


async def presigned_bundle_download_url(
    object_key: str,
    expires_seconds: Optional[int] = None,
) -> str:
    if not settings.MINIO_ENABLED:
        raise MinioUnavailable("MinIO dinonaktifkan di environment ini")
    seconds = expires_seconds or settings.PRESIGNED_EXPIRES_SECONDS

    def _do() -> str:
        return _get_client().presigned_get_object(
            settings.MINIO_BUCKET,
            object_key,
            expires=timedelta(seconds=seconds),
        )

    try:
        url = await _run_sync(_do)
    except S3Error as exc:
        raise MinioUnavailable(f"Presigned GET gagal: {exc}") from exc
    return _swap_endpoint_for_public(url)


async def delete_bundle_object(object_key: str) -> None:
    if not settings.MINIO_ENABLED:
        return

    def _do() -> None:
        _get_client().remove_object(settings.MINIO_BUCKET, object_key)

    try:
        await _run_sync(_do)
    except S3Error as exc:
        if exc.code in ("NoSuchKey", "NoSuchObject"):
            return
        raise MinioUnavailable(f"Hapus bundle gagal: {exc}") from exc


async def stream_bundle_object(object_key: str) -> AsyncIterator[bytes]:
    if not settings.MINIO_ENABLED:
        raise MinioUnavailable("MinIO dinonaktifkan di environment ini")
    import asyncio

    loop = asyncio.get_running_loop()

    def _open():
        return _get_client().get_object(settings.MINIO_BUCKET, object_key)

    response = await loop.run_in_executor(None, _open)
    try:
        while True:
            chunk = await loop.run_in_executor(None, response.read, 64 * 1024)
            if not chunk:
                break
            yield chunk
    finally:
        await loop.run_in_executor(None, response.close)
        await loop.run_in_executor(None, response.release_conn)

async def get_object_stream(object_key: str) -> Tuple[Any, int, str]:
    """
    Mengambil response stream objek dari MinIO.
    Mengembalikan: (response_stream, content_length, etag/checksum)
    """
    def _fetch():
        client = _get_client()
        bucket_name = str(
            getattr(settings, "target_bucket", None)
            or getattr(settings, "MINIO_BUCKET_NAME", None)
            or getattr(settings, "MINIO_BUCKET", None)
            or "opa-bundles-staging"
        ).strip()

        stat = client.stat_object(bucket_name, object_key)
        response = client.get_object(bucket_name, object_key)
        return response, stat.size, stat.etag.strip('"')

    return await asyncio.to_thread(_fetch)


async def get_presigned_download_url(object_key: str, expires_in_seconds: int = 3600) -> str:
    """Menghasilkan presigned download URL dari MinIO/S3 untuk object key tertentu."""
    def _get_url() -> str:
        client = _get_client()
        bucket_name = str(
            getattr(settings, "target_bucket", None)
            or getattr(settings, "MINIO_BUCKET_NAME", None)
            or getattr(settings, "MINIO_BUCKET", None)
            or "opa-bundles-staging"
        ).strip()

        # MinIO Python SDK presigned_get_object
        return client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_key,
            expires=timedelta(seconds=expires_in_seconds),
        )

    return await asyncio.to_thread(_get_url)