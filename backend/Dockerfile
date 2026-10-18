# ==========================================
# STAGE 1: Builder (Kompilasi Dependencies & Binary)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install dependensi sistem untuk build wheel C/Rust dan download utility
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download binary OPA CLI resmi untuk modul simulasi dry-run
ARG OPA_VERSION=v0.62.0
RUN curl -L -o /build/opa https://openpolicyagent.org/downloads/${OPA_VERSION}/opa_linux_amd64_static \
    && chmod 755 /build/opa

# Install dependensi Python ke direktori isolasi /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==========================================
# STAGE 2: Final Runtime
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install dependency runtime minimal (curl untuk Docker healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Buat grup dan pengguna non-root
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --no-create-home appuser

# Salin binary OPA CLI dari stage builder
COPY --from=builder /build/opa /usr/local/bin/opa

# Salin package Python yang sudah terpasang
COPY --from=builder /install /usr/local

# Salin source code aplikasi
COPY . /app

# Berikan kepemilikan file ke non-root user
RUN chown -R appuser:appgroup /app

# Atur environment variables Python standar container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:$PATH"

# Pindah ke non-root user
USER appuser

# Expose port aplikasi
EXPOSE 8000

# Healthcheck bawaan Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command default untuk runtime container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]