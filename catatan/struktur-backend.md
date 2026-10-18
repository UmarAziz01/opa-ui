backend/
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── .env
└── app/
    ├── main.py                     # Entrypoint FastAPI, CORS, middleware, global router
    │
    ├── core/                       # Konfigurasi dasar sistem
    │   ├── config.py               # Settings (Pydantic BaseSettings, env vars)
    │   ├── database.py             # SQLAlchemy Async Engine & Base
    │   ├── security.py             # Keycloak JWT verification, token decoding, PKCE
    │   └── storage.py              # MinIO Client instance & helpers
    │
    ├── common/                     # Utilitas reusable lintas modul
    │   ├── dependencies.py         # Global deps (get_db, get_current_user)
    │   ├── exceptions.py           # Custom exception & error handlers
    │   ├── pagination.py           # Skema pagination seragam
    │   └── utils.py                # Hashing, crypto, time helpers
    │
    ├── modules/                    # 8 Domain Modul OPA UI SaaS
    │   │
    │   ├── auth/                   # Modul 1: Identity & Keycloak OIDC
    │   │   ├── router.py           # Endpoint: /auth/login-callback, /auth/me
    │   │   ├── schemas.py          # UserClaims, TokenResponse
    │   │   ├── service.py          # Keycloak user sync logic
    │   │   └── models.py           # Table users
    │   │
    │   ├── tenants/                # Modul 2: Tenant & 30-Day Trial Lifecycle
    │   │   ├── router.py           # Endpoint: /tenants/register, /tenants/me
    │   │   ├── schemas.py          # TenantCreate, SubscriptionStatus
    │   │   ├── service.py          # Trial calculator, quota check logic
    │   │   └── models.py           # Table tenants, tenant_members
    │   │
    │   ├── organizations/          # Modul 3: Organizations & Scope Access
    │   │   ├── router.py           # Endpoint: /organizations, /members
    │   │   ├── schemas.py          # OrgCreate, MemberAssignRequest
    │   │   ├── service.py          # Scope verification, dev invitation
    │   │   └── models.py           # Table organizations, organization_members
    │   │
    │   ├── applications/           # Modul 4: Apps & Client Runtime
    │   │   ├── router.py           # Endpoint: /apps, /tokens
    │   │   ├── schemas.py          # AppCreate, TokenResponse
    │   │   ├── service.py          # Sidecar registry, service_tokens generator
    │   │   └── models.py           # Table applications, service_tokens
    │   │
    │   ├── policies/               # Modul 5: Policy Definition (RBAC Matrix)
    │   │   ├── router.py           # Endpoint: /roles, /permissions, /matrix
    │   │   ├── schemas.py          # RoleCreate, PermissionAssign, SimulatorPayload
    │   │   ├── service.py          # Policy matrix builder & simulation logic
    │   │   └── models.py           # Table roles, permissions, role_permissions, target_user_role_mappings
    │   │
    │   ├── bundles/                # Modul 6: OPA Bundler & MinIO Storage
    │   │   ├── router.py           # Endpoint: /bundles/build, /bundles/{id}/diff
    │   │   ├── schemas.py          # BundleResponse, DiffViewerResponse
    │   │   ├── service.py          # Tar.gz packaging, checksum calculation, MinIO upload
    │   │   └── models.py           # Table policy_bundles
    │   │
    │   ├── governance/             # Modul 7: Quality Gates, GitOps & Approvals
    │   │   ├── router.py           # Endpoint: /approvals, /approvals/{id}/review
    │   │   ├── schemas.py          # ApprovalRequestCreate, ReviewAction
    │   │   ├── service.py          # opa test runner (subprocess), approval state machine
    │   │   └── models.py           # Table bundle_approvals
    │   │
    │   └── audit/                  # Modul 8: Security & Audit Logging
    │       ├── router.py           # Endpoint: /audit-logs
    │       ├── schemas.py          # AuditLogFilter, AuditLogEntry
    │       ├── service.py          # Event emitter & JSONB change recorder
    │       └── models.py           # Table audit_logs
    │
    └── workers/                    # Background Jobs / Scheduled Tasks
        ├── bundle_compiler.py      # Async background bundle compilation
        └── trial_checker.py        # Cron runner auto-expire status trial 30 hari