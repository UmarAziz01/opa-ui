### 1. Struktur Folder File Bundle (`bundle.tar.gz`)

Setiap bundle yang dikompilasi dan diunggah ke MinIO berisi metadata manifest, file policy Rego, dan snapshot data JSON:

```text
bundle.tar.gz
├── .manifest                  # Metadata OPA (roots namespace & revision)
├── policies/
│   ├── core/
│   │   └── authz.rego         # Policy evaluator universal / inheritance
│   └── org/
│       └── rules.rego         # Rule spesifik organisasi (opsional jika ada custom logic)
└── data/
    └── tenants/
        └── {tenant_slug}/
            └── orgs/
                └── {org_slug}/
                    └── data.json   # Matriks RBAC & mapping user

```

---

### 2. Isi `.manifest`

Membatasi namespace data/policy yang di-*load* oleh bundle ini:

```json
{
  "revision": "v1.0.4",
  "roots": [
    "tenants/tenant_abc/orgs/ecommerce",
    "policies/authz"
  ]
}

```

---

### 3. Struktur `data.json` (Snapshot RBAC Organisasi)

Path root data di OPA akan tersimpan pada path `data.tenants[tenant_slug].orgs[org_slug]`:

```json
{
  "tenants": {
    "acme_corp": {
      "orgs": {
        "ecommerce": {
          "roles": {
            "catalog_editor": {
              "permissions": [
                "products:read",
                "products:create",
                "products:update"
              ]
            },
            "order_viewer": {
              "permissions": [
                "orders:read"
              ]
            }
          },
          "user_roles": {
            "usr_keycloak_uuid_101": ["catalog_editor"],
            "usr_keycloak_uuid_202": ["order_viewer"]
          }
        }
      }
    }
  }
}

```

---

### 4. Struktur Rule Rego Evaluator (`policies/core/authz.rego`)

Rule universal yang mengevaluasi izin secara bertingkat berdasarkan tenant, organisasi, action, dan resource:

```rego
package policies.authz

import rego.v1

default allow := false

# Input runtime dari microservice/sidecar:
# {
#   "tenant": "acme_corp",
#   "org": "ecommerce",
#   "user_id": "usr_keycloak_uuid_101",
#   "action": "create",
#   "resource": "products"
# }

allow if {
    # 1. Ambil data scope organisasi target
    org_data := data.tenants[input.tenant].orgs[input.org]

    # 2. Ambil role yang dimiliki user
    some role_name in org_data.user_roles[input.user_id]

    # 3. Ambil daftar permission milik role tersebut
    some permission in org_data.roles[role_name].permissions

    # 4. Validasi kecocokan permission string "resource:action"
    target_permission := concat(":", [input.resource, input.action])
    permission == target_permission
}

```

---

### 5. Struktur Penyimpanan Path Object di MinIO

Agar bundle rapi dan mendukung multi-environment serta versioning:

```text
opa-bundles/ (Bucket)
└── tenants/
    └── {tenant_slug}/
        └── {org_slug}/
            ├── staging/
            │   ├── current.tar.gz         # Symlink/pointer ke versi aktif
            │   ├── bundle_v1.tar.gz
            │   └── bundle_v2.tar.gz
            └── production/
                ├── current.tar.gz
                └── bundle_v1.tar.gz

```

* **OPA Sidecar Client** cukup menembak URL endpoint polling tetap:
`GET /bundles/tenants/{tenant_slug}/{org_slug}/{environment}/current.tar.gz`