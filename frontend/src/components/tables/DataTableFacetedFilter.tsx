"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface Option {
  label: string;
  value: string;
}

interface DataTableFacetedFilterProps {
  title: string;
  options: Option[];
  value?: string;
  onChange: (value: string) => void;
}

export function DataTableFacetedFilter({
  title,
  options,
  value,
  onChange,
}: DataTableFacetedFilterProps) {
  return (
    <Select
      value={value || "ALL"}
      onValueChange={(val: string | null) => {
        if (!val || val === "ALL") {
          onChange("");
        } else {
          onChange(val);
        }
      }}
    >
      <SelectTrigger className="w-[180px] h-8 text-xs">
        <SelectValue placeholder={title} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="ALL">Semua {title}</SelectItem>
        {options.map((opt) => (
          <SelectItem key={opt.value} value={opt.value}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}