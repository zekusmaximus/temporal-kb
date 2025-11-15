import { create } from 'zustand';
import { Entry } from '../types';

interface AppState {
  // Entries
  entries: Entry[];
  selectedEntry: Entry | null;
  setEntries: (entries: Entry[]) => void;
  setSelectedEntry: (entry: Entry | null) => void;
  addEntry: (entry: Entry) => void;
  updateEntry: (entry: Entry) => void;
  removeEntry: (id: string) => void;

  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  // Settings
  isDarkMode: boolean;
  toggleDarkMode: () => void;

  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

export const useStore = create<AppState>((set) => ({
  // Entries
  entries: [],
  selectedEntry: null,
  setEntries: (entries) => set({ entries }),
  setSelectedEntry: (entry) => set({ selectedEntry: entry }),
  addEntry: (entry) => set((state) => ({ entries: [entry, ...state.entries] })),
  updateEntry: (entry) =>
    set((state) => ({
      entries: state.entries.map((e) => (e.id === entry.id ? entry : e)),
      selectedEntry: state.selectedEntry?.id === entry.id ? entry : state.selectedEntry,
    })),
  removeEntry: (id) =>
    set((state) => ({
      entries: state.entries.filter((e) => e.id !== id),
      selectedEntry: state.selectedEntry?.id === id ? null : state.selectedEntry,
    })),

  // UI state
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Settings
  isDarkMode: false,
  toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),

  // Search
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),
}));
