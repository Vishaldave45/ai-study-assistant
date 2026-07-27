import apiClient from './client';
import type { SummaryRequest, SummaryResponse } from '../types/summary';

export const summaryApi = {
  /**
   * Generates a study summary grounded in document chunks.
   */
  generate: async (request: SummaryRequest): Promise<SummaryResponse> => {
    const response = await apiClient.post<SummaryResponse>('/summary', request);
    return response.data;
  },
};
