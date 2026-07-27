import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface UiState {
  theme: 'dark' | 'light';
  sidebarOpen: boolean;
  activeTab: 'files' | 'chat' | 'summaries' | 'usage';
}

const initialState: UiState = {
  theme: 'dark',
  sidebarOpen: true,
  activeTab: 'files',
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setActiveTab: (state, action: PayloadAction<'files' | 'chat' | 'summaries' | 'usage'>) => {
      state.activeTab = action.payload;
    },
  },
});

export const { toggleTheme, toggleSidebar, setActiveTab } = uiSlice.actions;
export default uiSlice.reducer;
