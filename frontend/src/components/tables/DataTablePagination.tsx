"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface DataTablePaginationProps {
  pageIndex: number;
  pageSize: number;
  totalCount?: number;
  onPageChange: (newPage: number) => void;
  hasMore?: boolean;
}

export function DataTablePagination({
  pageIndex,
  onPageChange,
  hasMore = false,
}: DataTablePaginationProps) {
  return (
    <div className="flex items-center justify-between px-2 py-4">
      <div className="text-xs text-muted-foreground">Halaman {pageIndex + 1}</div>
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(pageIndex - 1)}
          disabled={pageIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-1" /> Sebelumnya
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(pageIndex + 1)}
          disabled={!hasMore}
        >
          Selanjutnya <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}