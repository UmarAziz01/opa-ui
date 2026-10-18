import docker
from app.core.config import settings

docker_client = docker.DockerClient(base_url=settings.DOCKER_HOST)

async def deploy_opa_sidecar(tenant_slug: str, app_slug: str, sidecar_port: int, bundle_poll_url: str, token: str):
    container_name = f"opa-{tenant_slug}-{app_slug}"

    # Stop container lama jika sudah berjalan
    try:
        existing = docker_client.containers.get(container_name)
        existing.stop()
        existing.remove()
    except docker.errors.NotFound:
        pass

    # Jalankan container OPA dengan konfigurasi dinamis via command CLI
    container = docker_client.containers.run(
        image="openpolicyagent/opa:latest",
        name=container_name,
        detach=True,
        ports={"8181/tcp": sidecar_port},
        command=[
            "run",
            "--server",
            "--set", f"services.minio.url={settings.MINIO_ENDPOINT}",
            "--set", f"services.minio.credentials.bearer.token={token}",
            "--set", f"bundles.main.service=minio",
            "--set", f"bundles.main.resource={bundle_poll_url}",
            "--set", "bundles.main.polling.min_delay_seconds=10",
            "--set", "bundles.main.polling.max_delay_seconds=30"
        ],
        restart_policy={"Name": "unless-stopped"}
    )
    return container.id, container.status