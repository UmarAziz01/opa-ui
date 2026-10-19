"use client";

import { useState } from "react";
import { RoleItem } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface SubjectAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  roles: RoleItem[];
  onSubmit: (subject: string, roleId: string) => Promise<void>;
}

export function SubjectAssignmentModal({
  isOpen,
  onClose,
  roles,
  onSubmit,
}: SubjectAssignmentModalProps) {
  const [subject, setSubject] = useState("");
  const [roleId, setRoleId] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject || !roleId) return;

    try {
      setIsLoading(true);
      await onSubmit(subject, roleId);
      setSubject("");
      setRoleId("");
      onClose();
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Tugaskan Role ke Subjek</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="subject">Subject Identifier (Username/Email)</Label>
            <Input
              id="subject"
              placeholder="e.g. alice@internal.net"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="role">Pilih Role</Label>
            <Select
              value={roleId}
              onValueChange={(val) => setRoleId(val ?? "")}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Pilih role..." />
              </SelectTrigger>
              <SelectContent>
                {roles.map((r) => (
                  <SelectItem key={r.id} value={r.id}>
                    {r.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Batal
            </Button>
            <Button type="submit" disabled={isLoading || !subject || !roleId}>
              {isLoading ? "Menyimpan..." : "Tugaskan"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}