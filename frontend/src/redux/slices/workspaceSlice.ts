import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface WorkspaceState {
  activeWorkspaceId: string | null;
  searchQuery: string;
  selectedFileFormatFilter: string;
}

const getStoredWorkspaceId = () => {
  if (typeof localStorage !== 'undefined') {
    return localStorage.getItem('ai_study_active_workspace') || null;
  }
  return null;
};

const initialState: WorkspaceState = {
  activeWorkspaceId: getStoredWorkspaceId(),
  searchQuery: '',
  selectedFileFormatFilter: 'ALL',
};

export const workspaceSlice = createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    setActiveWorkspaceId: (state, action: PayloadAction<string | null>) => {
      state.activeWorkspaceId = action.payload;
      if (typeof localStorage !== 'undefined') {
        if (action.payload) {
          localStorage.setItem('ai_study_active_workspace', action.payload);
        } else {
          localStorage.removeItem('ai_study_active_workspace');
        }
      }
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    setSelectedFileFormatFilter: (state, action: PayloadAction<string>) => {
      state.selectedFileFormatFilter = action.payload;
    },
  },
});

export const { setActiveWorkspaceId, setSearchQuery, setSelectedFileFormatFilter } =
  workspaceSlice.actions;
export default workspaceSlice.reducer;
