"use client";

import Editor, { OnMount } from "@monaco-editor/react";
import { Loader2 } from "lucide-react";

interface RegoEditorProps {
  value: string;
  onChange?: (val: string) => void;
  readOnly?: boolean;
  height?: string;
}

export function RegoEditor({
  value,
  onChange,
  readOnly = false,
  height = "400px",
}: RegoEditorProps) {
  const handleMount: OnMount = (editor, monaco) => {
    // Daftarkan tokenizer syntax highlighter sederhana untuk Open Policy Agent (Rego)
    monaco.languages.register({ id: "rego" });
    monaco.languages.setMonarchTokensProvider("rego", {
      keywords: ["package", "import", "default", "allow", "not", "with", "as", "some", "every", "in"],
      tokenizer: {
        root: [
          [/[a-z_$][\w$]*/, { cases: { "@keywords": "keyword", "@default": "identifier" } }],
          [/#.*$/, "comment"],
          [/"([^"\\]|\\.)*"/, "string"],
          [/\d+/, "number"],
        ],
      },
    });
  };

  return (
    <div className="w-full rounded-md border border-border overflow-hidden">
      <Editor
        height={height}
        language="rego"
        theme="vs-dark"
        value={value}
        onChange={(val) => onChange?.(val || "")}
        onMount={handleMount}
        loading={<Loader2 className="h-6 w-6 animate-spin text-muted-foreground m-auto" />}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          tabSize: 2,
        }}
      />
    </div>
  );
}