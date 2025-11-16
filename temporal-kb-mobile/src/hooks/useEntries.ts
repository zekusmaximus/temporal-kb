import { useState, useCallback } from 'react';
import { apiClient } from '../api/client';
import { useStore } from '../store';
import { Entry, EntryCreate, SearchParams } from '../types';
import { getErrorMessage } from '@/utils/errors';

interface UseEntriesReturn {
  loadEntries: (params?: SearchParams) => Promise<Entry[]>;
  loadRecent: (limit?: number) => Promise<Entry[]>;
  searchEntries: (query: string, params?: Omit<SearchParams, 'q'>) => Promise<Entry[]>;
  createEntry: (data: EntryCreate) => Promise<Entry>;
  updateEntry: (id: string, data: Partial<EntryCreate>) => Promise<Entry>;
  deleteEntry: (id: string) => Promise<void>;
  error: string | null;
}

export const useEntries = (): UseEntriesReturn => {
  const { setEntries, addEntry, updateEntry, removeEntry, setIsLoading } = useStore();
  const [error, setError] = useState<string | null>(null);

  const loadEntries = useCallback(
    async (params?: SearchParams): Promise<Entry[]> => {
      try {
        setIsLoading(true);
        setError(null);
        const entries = await apiClient.getEntries(params);
        setEntries(entries);
        return entries;
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Failed to load entries');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, setEntries]
  );

  const loadRecent = useCallback(
    async (limit: number = 20): Promise<Entry[]> => {
      try {
        setIsLoading(true);
        setError(null);
        const entries = await apiClient.getRecent(limit);
        setEntries(entries);
        return entries;
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Failed to load recent entries');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, setEntries]
  );

  const searchEntries = useCallback(
    async (query: string, params?: Omit<SearchParams, 'q'>): Promise<Entry[]> => {
      try {
        setIsLoading(true);
        setError(null);
        const entries = await apiClient.search(query, params);
        setEntries(entries);
        return entries;
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Search failed');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, setEntries]
  );

  const createEntry = useCallback(
    async (data: EntryCreate): Promise<Entry> => {
      try {
        setIsLoading(true);
        setError(null);
        const entry = await apiClient.createEntry(data);
        addEntry(entry);
        return entry;
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Failed to create entry');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, addEntry]
  );

  const updateEntryById = useCallback(
    async (id: string, data: Partial<EntryCreate>): Promise<Entry> => {
      try {
        setIsLoading(true);
        setError(null);
        const entry = await apiClient.updateEntry(id, data);
        updateEntry(entry);
        return entry;
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Failed to update entry');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, updateEntry]
  );

  const deleteEntry = useCallback(
    async (id: string): Promise<void> => {
      try {
        setIsLoading(true);
        setError(null);
        await apiClient.deleteEntry(id);
        removeEntry(id);
      } catch (err: unknown) {
        const message = getErrorMessage(err);
        setError(message || 'Failed to delete entry');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, removeEntry]
  );

  return {
    loadEntries,
    loadRecent,
    searchEntries,
    createEntry,
    updateEntry: updateEntryById,
    deleteEntry,
    error,
  };
};
