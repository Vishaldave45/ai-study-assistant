import { describe, it, expect } from 'vitest';
import uiReducer, { toggleTheme, toggleSidebar, setActiveTab } from './uiSlice';

describe('uiSlice Reducer', () => {
  it('handles initial state correctly', () => {
    const state = uiReducer(undefined, { type: 'unknown' });
    expect(state).toEqual({
      theme: 'dark',
      sidebarOpen: true,
      activeTab: 'files',
    });
  });

  it('toggles theme between dark and light', () => {
    const state1 = uiReducer(undefined, toggleTheme());
    expect(state1.theme).toBe('light');

    const state2 = uiReducer(state1, toggleTheme());
    expect(state2.theme).toBe('dark');
  });

  it('toggles sidebar visibility flag', () => {
    const state1 = uiReducer(undefined, toggleSidebar());
    expect(state1.sidebarOpen).toBe(false);

    const state2 = uiReducer(state1, toggleSidebar());
    expect(state2.sidebarOpen).toBe(true);
  });

  it('sets active tab state with setActiveTab', () => {
    const state = uiReducer(undefined, setActiveTab('chat'));
    expect(state.activeTab).toBe('chat');
  });
});
