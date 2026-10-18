import asyncio
import logging
from typing import AsyncIterator, Dict, Any
import docker
import httpx
from docker.errors import NotFound, APIError
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

_docker_client: Any = None


def get_docker_client() -> docker.DockerClient:
    global _docker_client
    if _docker_client is None:
        try:
            _docker_client = docker.DockerClient(base_url=settings.DOCKER_HOST)
            _docker_client.ping()
        except Exception as exc:
            logger.error("Gagal terhubung ke Docker daemon di %s: %s", settings.DOCKER_HOST, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Docker Engine daemon host tidak dapat dijangkau oleh backend.",
            )
    return _docker_client


def _ensure_network_sync(client: docker.DockerClient, network_name: str) -> None:
    try:
        client.networks.get(network_name)
    except NotFound:
        logger.info("Docker network '%s' tidak ditemukan, membuat network bridge baru...", network_name)
        client.networks.create(network_name, driver="bridge")


def _spawn_opa_container_sync(
    tenant_slug: str,
    org_slug: str,
    app_slug: str,
    assigned_port: int,
    service_token: str,
    environment: str = "production",
) -> Dict[str, Any]:
    client = get_docker_client()
    network_name = getattr(settings, "DOCKER_NETWORK", "opa-staging-network")
    _ensure_network_sync(client, network_name)

    container_name = f"opa-{tenant_slug}-{org_slug}-{app_slug}"
    bundle_resource_path = f"/bundles/tenants/{tenant_slug}/orgs/{org_slug}/{environment}/current.tar.gz"

    # Hentikan dan bersihkan container lama jika ada
    try:
        old_container = client.containers.get(container_name)
        old_container.stop(timeout=3)
        old_container.remove(force=True)
    except NotFound:
        pass
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mereset container lama: {exc.explanation}",
        )

    # Argumen OPA server dengan MinIO bundle polling
    minio_host_url = f"http://{settings.MINIO_ENDPOINT}"
    opa_command = [
        "run",
        "--server",
        "--addr=0.0.0.0:8181",
        "--set", f"services.minio_bundle_svc.url={minio_host_url}",
        "--set", f"services.minio_bundle_svc.credentials.bearer.token={service_token}",
        "--set", "bundles.authz_bundle.service=minio_bundle_svc",
        "--set", f"bundles.authz_bundle.resource={bundle_resource_path}",
        "--set", "bundles.authz_bundle.polling.min_delay_seconds=10",
        "--set", "bundles.authz_bundle.polling.max_delay_seconds=30",
    ]

    try:
        container = client.containers.run(
            image="openpolicyagent/opa:latest",
            name=container_name,
            command=opa_command,
            detach=True,
            network=network_name,
            ports={"8181/tcp": assigned_port},
            restart_policy={"Name": "unless-stopped"},
            labels={
                "managed_by": "opa-ui-saas",
                "tenant": tenant_slug,
                "org": org_slug,
                "app": app_slug,
                "environment": environment,
            },
        )
        return {
            "container_id": container.id,
            "container_name": container_name,
            "status": "running",
            "host_port": assigned_port,
            "network": network_name,
        }
    except APIError as exc:
        logger.error("Gagal menjalankan container OPA %s: %s", container_name, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Docker API Error saat spawn OPA: {exc.explanation}",
        )


async def spawn_opa_sidecar(
    tenant_slug: str,
    org_slug: str,
    app_slug: str,
    assigned_port: int,
    service_token: str,
    environment: str = "production",
) -> Dict[str, Any]:
    return await asyncio.to_thread(
        _spawn_opa_container_sync,
        tenant_slug,
        org_slug,
        app_slug,
        assigned_port,
        service_token,
        environment,
    )


async def stop_opa_sidecar(container_name: str) -> bool:
    def _stop() -> bool:
        client = get_docker_client()
        try:
            container = client.containers.get(container_name)
            container.stop(timeout=5)
            container.remove(force=True)
            return True
        except NotFound:
            return False
        except APIError:
            return False

    return await asyncio.to_thread(_stop)


async def get_opa_container_health(
    tenant_slug: str,
    org_slug: str,
    app_slug: str,
    assigned_port: int,
) -> Dict[str, Any]:
    container_name = f"opa-{tenant_slug}-{org_slug}-{app_slug}"

    def _inspect_docker():
        client = get_docker_client()
        try:
            container = client.containers.get(container_name)
            return {"exists": True, "status": container.status}
        except NotFound:
            return {"exists": False, "status": "not_found"}
        except APIError as exc:
            return {"exists": False, "status": "error", "error": exc.explanation}

    info = await asyncio.to_thread(_inspect_docker)
    if not info["exists"] or info["status"] != "running":
        return {
            "container_name": container_name,
            "docker_status": info["status"],
            "opa_engine_ready": False,
            "port": assigned_port,
            "message": "Kontainer OPA tidak berjalan di Docker host.",
        }

    # Ping endpoint /health OPA internal
    opa_health_url = f"http://127.0.0.1:{assigned_port}/health"
    ready = False
    message = "Healthy"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(opa_health_url)
            ready = (resp.status_code == 200)
            if not ready:
                message = f"OPA merespon HTTP {resp.status_code}"
    except httpx.RequestError as exc:
        message = f"OPA endpoint tidak merespon: {str(exc)}"

    return {
        "container_name": container_name,
        "docker_status": info["status"],
        "opa_engine_ready": ready,
        "port": assigned_port,
        "message": message,
    }


async def restart_opa_container(
    tenant_slug: str,
    org_slug: str,
    app_slug: str,
) -> Dict[str, Any]:
    container_name = f"opa-{tenant_slug}-{org_slug}-{app_slug}"

    def _restart():
        client = get_docker_client()
        try:
            container = client.containers.get(container_name)
            container.restart(timeout=10)
            container.reload()
            return {"status": "restarted", "current_status": container.status}
        except NotFound:
            raise HTTPException(status_code=404, detail=f"Kontainer {container_name} tidak ditemukan.")
        except APIError as exc:
            raise HTTPException(status_code=500, detail=f"Docker restart gagal: {exc.explanation}")

    return await asyncio.to_thread(_restart)


async def stream_container_logs(
    tenant_slug: str,
    org_slug: str,
    app_slug: str,
    tail: int = 100,
) -> AsyncIterator[str]:
    container_name = f"opa-{tenant_slug}-{org_slug}-{app_slug}"
    client = get_docker_client()

    try:
        container = client.containers.get(container_name)
    except NotFound:
        yield f"event: error\ndata: Kontainer {container_name} tidak ditemukan.\n\n"
        return
    except APIError as exc:
        yield f"event: error\ndata: Docker API error: {exc.explanation}\n\n"
        return

    log_stream = container.logs(
        stdout=True,
        stderr=True,
        stream=True,
        follow=True,
        tail=tail,
        timestamps=True,
    )

    loop = asyncio.get_running_loop()
    try:
        while True:
            chunk = await loop.run_in_executor(None, next, log_stream, None)
            if chunk is None:
                break
            line_text = chunk.decode("utf-8", errors="replace").strip()
            if line_text:
                yield f"data: {line_text}\n\n"
    except asyncio.CancelledError:
        logger.info("Log stream ditutup untuk %s", container_name)
    finally:
        if hasattr(log_stream, "close"):
            log_stream.close()