"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { RegoEditor } from "@/components/editor/RegoEditor";
import { Button } from "@/components/ui/button";
import { Play, Save } from "lucide-react";

const DEFAULT_REGO = `package authz

default allow = false

# Rule default RBAC
allow if {
    some role in input.user.roles
    permission := data.role_permissions[role][_]
    permission.resource == input.resource
    permission.action == input.action
}
`;

export default function RegoEditorPage() {
  const [code, setCode] = useState(DEFAULT_REGO);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold tracking-tight">Monaco Rego Editor</h3>
          <p className="text-xs text-muted-foreground">Tulis dan uji coba aturan policy Rego v1 secara interaktif.</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline">
            <Play className="h-3.5 w-3.5 mr-1" /> Test Syntax
          </Button>
          <Button size="sm">
            <Save className="h-3.5 w-3.5 mr-1" /> Simpan Policy
          </Button>
        </div>
      </div>

      <RegoEditor value={code} onChange={setCode} height="520px" />
    </div>
  );
}