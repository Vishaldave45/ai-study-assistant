import { describe, it, expect } from 'vitest';
import type { ExtendedResponse } from '../base-axios/types';

describe('useAxios response transformer utility', () => {
  it('formats successful API response correctly', () => {
    const mockData = { id: 'ws-123', name: 'Study Workspace' };
    const extendedResp: ExtendedResponse<typeof mockData> = {
      isSuccess: true,
      data: mockData,
      status: 200,
      statusText: 'OK',
      error: null,
    };

    expect(extendedResp.isSuccess).toBe(true);
    expect(extendedResp.data.id).toBe('ws-123');
    expect(extendedResp.error).toBeNull();
  });

  it('formats API error response correctly', () => {
    const extendedResp: ExtendedResponse<null> = {
      isSuccess: false,
      data: null,
      status: 400,
      statusText: 'Bad Request',
      error: 'Invalid workspace ID',
    };

    expect(extendedResp.isSuccess).toBe(false);
    expect(extendedResp.error).toBe('Invalid workspace ID');
  });
});
