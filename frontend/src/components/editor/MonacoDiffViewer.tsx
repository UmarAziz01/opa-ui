"use client";

import { DiffEditor } from "@monaco-editor/react";
import { Loader2 } from "lucide-react";

interface MonacoDiffViewerProps {
  original: string;
  modified: string;
  height?: string;
  language?: string;
}

export function MonacoDiffViewer({
  original,
  modified,
  height = "450px",
  language = "rego",
}: MonacoDiffViewerProps) {
  return (
    <div className="w-full rounded-md border border-border overflow-hidden">
      <DiffEditor
        height={height}
        language={language}
        theme="vs-dark"
        original={original}
        modified={modified}
        loading={<Loader2 className="h-6 w-6 animate-spin text-muted-foreground m-auto" />}
        options={{
          readOnly: true,
          renderSideBySide: true,
          minimap: { enabled: false },
          fontSize: 13,
        }}
      />
    </div>
  );
}