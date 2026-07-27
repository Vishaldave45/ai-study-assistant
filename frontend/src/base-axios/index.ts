import axios, { AxiosError } from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, ACCESS_TOKEN_KEY } from '../config';
import type { ApiErrorResponse } from './types';

/**
 * Single configured Axios instance for the app.
 * Follows react-ts-boilerplate-main base-axios architecture.
 */
export const Axios: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// REQUEST Interceptor: Attach bearer token automatically
Axios.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// RESPONSE Interceptor: Auto-logout on 401 Unauthorized
Axios.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    const status = error.response?.status;
    if (status === 401) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      window.dispatchEvent(new Event('auth:logout'));
    }
    return Promise.reject(error);
  }
);

export default Axios;
