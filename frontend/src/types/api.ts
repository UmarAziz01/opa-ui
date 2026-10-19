export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}

export interface ApiErrorResponse {
  detail: string | ApiValidationError[];
}

export interface PaginationParams {
  limit?: number;
  offset?: number;
}