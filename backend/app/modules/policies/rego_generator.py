import json
from typing import Any, Dict, List
from app.modules.policies.models import Role, TargetUserRoleMapping


def generate_rego_policy(org_slug: str) -> str:
    """
    Menghasilkan kode Rego v1 murni untuk otorisasi RBAC multi-tenant.
    Query default: data.org.<org_slug>.authz.allow
    """
    sanitized_slug = org_slug.replace("-", "_")
    rego_code = f"""package org.{sanitized_slug}.authz

import rego.v1

# Default keputusan ditolak
default allow := false

# Rule 1: Izinkan jika subjek memiliki role yang memiliki izin pada resource & action terkait
allow if {{
    user_roles := data.user_roles[input.subject]
    some role_name in user_roles
    role_perms := data.role_permissions[role_name]
    some perm in role_perms
    perm.resource == input.resource
    perm.action == input.action
}}

# Rule 2: Superadmin bypass otomatis jika didefinisikan di context
allow if {{
    input.context.is_superadmin == true
}}
"""
    return rego_code


def build_opa_data_json(
    roles: List[Role],
    mappings: List[TargetUserRoleMapping],
) -> Dict[str, Any]:
    """
    Menyusun pohon data JSON yang akan dibaca OPA engine:
    {
      "role_permissions": { "RoleA": [ {"resource": "x", "action": "y"} ] },
      "user_roles": { "alice": ["RoleA"] }
    }
    """
    role_permissions_dict: Dict[str, List[Dict[str, str]]] = {}
    for r in roles:
        role_permissions_dict[r.name] = [
            {"resource": p.resource, "action": p.action}
            for p in r.permissions
        ]

    user_roles_dict: Dict[str, List[str]] = {}
    for m in mappings:
        # Menghubungkan identifier subjek ke nama role
        role_name = m.role.name if m.role else None
        if not role_name:
            continue
        if m.subject_identifier not in user_roles_dict:
            user_roles_dict[m.subject_identifier] = []
        if role_name not in user_roles_dict[m.subject_identifier]:
            user_roles_dict[m.subject_identifier].append(role_name)

    return {
        "role_permissions": role_permissions_dict,
        "user_roles": user_roles_dict,
    }