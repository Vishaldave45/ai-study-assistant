import apiClient from '../api/client';

/**
 * Single consolidated Axios instance with silent 401 token refresh queue logic.
 */
export const Axios = apiClient;
export default apiClient;
