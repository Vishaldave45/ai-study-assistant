import { describe, it, expect, beforeEach } from 'vitest';
import workspaceReducer, {
  setActiveWorkspaceId,
  setSearchQuery,
  setSelectedFileFormatFilter,
} from './workspaceSlice';

describe('workspaceSlice Reducer', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('handles initial state correctly', () => {
    const state = workspaceReducer(undefined, { type: 'unknown' });
    expect(state).toEqual({
      activeWorkspaceId: null,
      searchQuery: '',
      selectedFileFormatFilter: 'ALL',
    });
  });

  it('updates active workspace ID and persists to localStorage', () => {
    const state = workspaceReducer(undefined, setActiveWorkspaceId('ws-999'));
    expect(state.activeWorkspaceId).toBe('ws-999');
    expect(localStorage.getItem('ai_study_active_workspace')).toBe('ws-999');

    const clearedState = workspaceReducer(state, setActiveWorkspaceId(null));
    expect(clearedState.activeWorkspaceId).toBeNull();
    expect(localStorage.getItem('ai_study_active_workspace')).toBeNull();
  });

  it('updates search query state with setSearchQuery', () => {
    const state = workspaceReducer(undefined, setSearchQuery('quantum physics'));
    expect(state.searchQuery).toBe('quantum physics');
  });

  it('updates file format filter with setSelectedFileFormatFilter', () => {
    const state = workspaceReducer(undefined, setSelectedFileFormatFilter('PDF'));
    expect(state.selectedFileFormatFilter).toBe('PDF');
  });
});
