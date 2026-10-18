### Daftar Fitur Lengkap per Modul

#### Modul 1: Identity & Authentication (Keycloak OIDC Integration)

* **Single Sign-On (SSO):** Login/Logout via Keycloak OIDC (Authorization Code Flow + PKCE).
* **Claim Mapping Sync:** Sinkronisasi otomatis token claims (`sub`, `email`, `preferred_username`) ke tabel `users`.
* **User Lifecycle Management:** Status akun pengguna (`ACTIVE`, `INACTIVE`, `SUSPENDED`) tersinkronisasi.
* **Superadmin / Root View:** Akses pemeliharaan global khusus pengguna dengan tipe `Internal`.

#### Modul 2: Tenant & Subscription Lifecycle (Self-Service 30-Day Trial)

* **Self-Service Onboarding:** Form pendaftaran mandiri yang langsung membuat tenant, inisialisasi membership owner, dan mengaktifkan trial 30 hari.
* **Trial Expiration Engine:** Cron/background worker pengecek `trial_ends_at` otomatis mengubah status menjadi `EXPIRED` dan mengunci build bundle baru.
* **Resource Quota Enforcement:** Pembatasan kuota organisasi (`max_organizations`) dan developer (`max_developers`) sesuai tier aktif.
* **Tenant Member Management:** Pengelolaan staf tenant dengan peran `TENANT_ADMIN` atau `TENANT_MEMBER`.

#### Modul 3: Organization & Scoped Access Control

* **Organizational Segmentation:** Pembuatan sub-organisasi/divisi per tenant untuk isolasi domain data.
* **Developer Membership Delegation:** Admin Tenant / Org menugaskan developer ke organisasi tertentu dengan hak `DEVELOPER`, `ORG_ADMIN`, atau `VIEWER`.
* **Workspace Isolation Filter:** Dashboard otomatis memfilter organisasi dan aplikasi sesuai hak akses pengguna yang sedang login.

#### Modul 4: Application & Client Runtime Configuration

* **Service Registry:** Pendaftaran microservice/aplikasi (`applications`) di bawah organisasi.
* **Sidecar Parameter Setup:** Konfigurasi port OPA sidecar (`sidecar_port`), flag pewarisan aturan global (`inherits_from_core`), dan asymmetric signing keys.
* **Runtime Authentication (Service Tokens):** Pembuatan dan rotasi Bearer token/API Key bagi OPA client untuk mengunduh bundle.

#### Modul 5: Policy Definition (RBAC & Permission Matrix)

* **Permission Catalog:** Pendaftaran resource dan aksi (`action` + `resource`, misal `orders:create`, `invoices:approve`).
* **Interactive Matrix Editor:** Antarmuka visual checklist role vs permission per organisasi.
* **Target Subject Mapping:** Penetapan role ke user akhir aplikasi tenant via `subject_identifier`.
* **Policy Simulator (Dry Run):** Pengujian payload JSON tiruan (`input`) langsung di UI untuk melihat evaluasi izin (`allow: true/false`).

#### Modul 6: OPA Bundle Engine & MinIO Integration

* **Bundle Compiler Worker:** Mengompilasi data tabel relational dan skema Rego menjadi bundle `bundle.tar.gz`.
* **MinIO Artifact Storage:** Upload bundle dengan penamaan terstruktur, checksum SHA256, dan versi incremental.
* **Environment Separation:** Pemisahan deployment bundle untuk target `staging` dan `production`.
* **Snapshot & Diff Viewer:** Penyimpanan payload JSON mentah (`snapshot_data`) untuk visualisasi perubahan (*side-by-side diff*) antar versi tanpa extract file.

#### Modul 7: Governance, GitOps & Release Quality Gates

* **Automated Unit Testing Gate:** Eksekusi otomatis `opa test` sebelum bundle disetujui; menyimpan log `test_output` dan status `test_passed`.
* **GitOps Traceability:** Pencatatan `git_commit` dan `file_diff` untuk keterlacakan revisi Git.
* **Release Approval Workflow:**
* Developer mengajukan permohonan rilis ke environment produksi (`PENDING`).
* Admin meninjau diff dan memberikan keputusan (`APPROVED` / `REJECTED`) disertai catatan evaluasi.


* **Rollback Engine:** Opsi instan mengembalikan pointer bundle aktif ke `parent_bundle_id` versi sebelumnya jika ditemukan anomali.

#### Modul 8: Security & Audit Logging

* **Immutable Audit Trail:** Pencatatan otomatis setiap aksi administratif (`ROLE_CREATED`, `PERMISSION_ATTACHED`, `BUNDLE_BUILT`, `APPROVAL_GRANTED`).
* **State Diff Capture:** Menyimpan snapshot sebelum dan sesudah perubahan dalam format `JSONB`.