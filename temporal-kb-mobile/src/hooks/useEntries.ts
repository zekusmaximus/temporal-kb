import { useState, useCallback } from 'react';
import { apiClient } from '../api/client';
import { useStore } from '../store';
import { Entry, EntryCreate, SearchParams } from '../types';

export const useEntries = () => {
  const { setEntries, addEntry, updateEntry, removeEntry, setIsLoading } = useStore();
  const [error, setError] = useState<string | null>(null);

  const loadEntries = useCallback(async (params?: SearchParams) => {
    try {
      setIsLoading(true);
      setError(null);
      const entries = await apiClient.getEntries(params);
      setEntries(entries);
      return entries;
    } catch (err: any) {
      setError(err.message || 'Failed to load entries');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadRecent = useCallback(async (limit: number = 20) => {
    try {
      setIsLoading(true);
      setError(null);
      const entries = await apiClient.getRecent(limit);
      setEntries(entries);
      return entries;
    } catch (err: any) {
      setError(err.message || 'Failed to load recent entries');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const searchEntries = useCallback(async (query: string, params?: Omit<SearchParams, 'q'>) => {
    try {
      setIsLoading(true);
      setError(null);
      const entries = await apiClient.search(query, params);
      setEntries(entries);
      return entries;
    } catch (err: any) {
      setError(err.message || 'Search failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createEntry = useCallback(async (data: EntryCreate) => {
    try {
      setIsLoading(true);
      setError(null);
      const entry = await apiClient.createEntry(data);
      addEntry(entry);
      return entry;
    } catch (err: any) {
      setError(err.message || 'Failed to create entry');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateEntryById = useCallback(async (id: string, data: Partial<EntryCreate>) => {
    try {
      setIsLoading(true);
      setError(null);
      const entry = await apiClient.updateEntry(id, data);
      updateEntry(entry);
      return entry;
    } catch (err: any) {
      setError(err.message || 'Failed to update entry');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteEntry = useCallback(async (id: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await apiClient.deleteEntry(id);
      removeEntry(id);
    } catch (err: any) {
      setError(err.message || 'Failed to delete entry');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

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
