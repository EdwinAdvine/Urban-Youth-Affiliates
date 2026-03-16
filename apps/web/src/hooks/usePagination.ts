import { useState } from "react";

export interface PaginationState {
  page: number;
  pageSize: number;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  reset: () => void;
}

export function usePagination(defaultPageSize: number = 20): PaginationState {
  const [page, setPageRaw] = useState(1);
  const [pageSize, setPageSizeRaw] = useState(defaultPageSize);

  const setPage = (p: number) => setPageRaw(Math.max(1, p));
  const setPageSize = (s: number) => {
    setPageSizeRaw(s);
    setPageRaw(1);
  };
  const reset = () => {
    setPageRaw(1);
  };

  return { page, pageSize, setPage, setPageSize, reset };
}
