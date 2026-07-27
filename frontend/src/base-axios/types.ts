import type { AxiosResponse, RawAxiosResponseHeaders, AxiosResponseHeaders } from 'axios';

/**
 * Unified shape returned by EVERY useAxios call (get/post/put/patch/delete).
 */
export interface ExtendedResponse<T = unknown> {
  isSuccess: boolean;
  data: T;
  message?: string;
  status?: number;
  statusText?: string;
  headers?: RawAxiosResponseHeaders | AxiosResponseHeaders;
  response?: AxiosResponse;
  error: string | null;
}

/** Standard error envelope the backend returns. */
export interface ApiErrorResponse {
  message?: string;
  detail?: string | Record<string, unknown>;
  data?: {
    message?: string;
    [key: string]: unknown;
  };
}
