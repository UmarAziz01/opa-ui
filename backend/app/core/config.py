import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App & Runtime
    APP_ENV: str = "local"
    DEBUG: bool = False
    APP_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "temporary-secret-key-change-me"

    # Sidecar Dynamic Port Allocation
    OPA_PORT_RANGE_START: int = 18100
    OPA_PORT_RANGE_END: int = 18999

    # Database PostgreSQL
    DATABASE_URL: str

    # Keycloak OIDC Authentication
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_USERNAME: str
    KEYCLOAK_ADMIN_PASSWORD: str

    # MinIO / S3 Storage Settings
    MINIO_ENABLED: bool = True
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_PUBLIC_ENDPOINT: str = "https://api-minio.sinflab.my.id"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "opa-bundles-staging"
    MINIO_BUCKET: Optional[str] = None
    MINIO_SECURE: bool = True
    MINIO_USE_SSL: bool = False
    MINIO_REGION: Optional[str] = "us-east-1"
    MINIO_PUBLIC_ENDPOINT: str = "https://api-minio.sinflab.my.id"
    PRESIGNED_EXPIRES_SECONDS: int = 60

    # Docker Integration
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    DOCKER_NETWORK: str = "opa-runtime-network"

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'local')}",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()

    @property
    def target_bucket(self) -> str:
        """Mengambil nama bucket yang aktif."""
        return self.MINIO_BUCKET or self.MINIO_BUCKET_NAME

    @property
    def is_secure(self) -> bool:
        """Sinkronisasi antara flag SECURE dan USE_SSL."""
        return self.MINIO_SECURE or self.MINIO_USE_SSL


settings = get_settings()