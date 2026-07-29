/**
 * Application-wide configuration variables.
 */
export const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) || '/api/v1';
export const ACCESS_TOKEN_KEY = 'ai_study_access_token';
export const REFRESH_TOKEN_KEY = 'ai_study_refresh_token';
