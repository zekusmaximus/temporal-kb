import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Entry, EntryCreate, SearchParams, SemanticSearchResult, RelatedEntry } from '../types';

const STORAGE_KEYS = {
  API_URL: '@temporal_kb:api_url',
  API_KEY: '@temporal_kb:api_key',
};

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded';
  version?: string;
  timestamp?: string;
}

export interface Tag {
  name: string;
  count: number;
}

export interface Project {
  name: string;
  entry_count: number;
}

export interface Stats {
  total_entries: number;
  total_words: number;
  tags_count: number;
  projects_count: number;
}

export interface ApiConfig {
  baseUrl: string;
  apiKey: string;
}

class TemporalKBClient {
  private client: AxiosInstance;
  private baseUrl: string = '';
  private apiKey: string = '';

  constructor() {
    this.client = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for API key
    this.client.interceptors.request.use(
      (config) => {
        if (this.apiKey) {
          config.headers['X-API-Key'] = this.apiKey;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          console.error('Unauthorized - check API key');
        }
        return Promise.reject(error);
      }
    );
  }

  async initialize(): Promise<void> {
    const [url, key] = await Promise.all([
      AsyncStorage.getItem(STORAGE_KEYS.API_URL),
      AsyncStorage.getItem(STORAGE_KEYS.API_KEY),
    ]);

    if (url) this.baseUrl = url;
    if (key) this.apiKey = key;

    this.client.defaults.baseURL = this.baseUrl;
  }

  async setConfig(baseUrl: string, apiKey: string): Promise<void> {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.client.defaults.baseURL = baseUrl;

    await Promise.all([
      AsyncStorage.setItem(STORAGE_KEYS.API_URL, baseUrl),
      AsyncStorage.setItem(STORAGE_KEYS.API_KEY, apiKey),
    ]);
  }

  async getConfig(): Promise<ApiConfig> {
    return {
      baseUrl: this.baseUrl,
      apiKey: this.apiKey,
    };
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.client.get<HealthCheckResponse>('/health');
    return response.data;
  }

  // Entries
  async getEntries(params?: SearchParams): Promise<Entry[]> {
    const response = await this.client.get('/api/v1/search', { params });
    return response.data;
  }

  async getEntry(id: string): Promise<Entry> {
    const response = await this.client.get(`/api/v1/entries/${id}`);
    return response.data;
  }

  async createEntry(data: EntryCreate): Promise<Entry> {
    const response = await this.client.post('/api/v1/entries', data);
    return response.data;
  }

  async updateEntry(id: string, data: Partial<EntryCreate>): Promise<Entry> {
    const response = await this.client.put(`/api/v1/entries/${id}`, data);
    return response.data;
  }

  async deleteEntry(id: string): Promise<void> {
    await this.client.delete(`/api/v1/entries/${id}`);
  }

  // Search
  async search(query: string, params?: Omit<SearchParams, 'q'>): Promise<Entry[]> {
    const response = await this.client.get('/api/v1/search', {
      params: { q: query, ...params },
    });
    return response.data;
  }

  async semanticSearch(query: string, limit: number = 10): Promise<SemanticSearchResult[]> {
    const response = await this.client.get('/api/v1/search/semantic', {
      params: { q: query, limit },
    });
    return response.data;
  }

  async getRecent(limit: number = 20): Promise<Entry[]> {
    const response = await this.client.get('/api/v1/search/recent', {
      params: { limit },
    });
    return response.data;
  }

  // Links
  async getRelatedEntries(entryId: string, maxResults: number = 10): Promise<RelatedEntry[]> {
    const response = await this.client.get(`/api/v1/links/${entryId}/related`, {
      params: { max_results: maxResults },
    });
    return response.data;
  }

  // Temporal
  async getOnThisDay(): Promise<Entry[]> {
    const response = await this.client.get('/api/v1/temporal/on-this-day');
    return response.data;
  }

  // Tags
  async getTags(): Promise<Tag[]> {
    const response = await this.client.get<Tag[]>('/api/v1/tags');
    return response.data;
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    const response = await this.client.get<Project[]>('/api/v1/projects');
    return response.data;
  }

  // Stats
  async getStats(): Promise<Stats> {
    const response = await this.client.get<Stats>('/api/v1/stats/overview');
    return response.data;
  }
}

export const apiClient = new TemporalKBClient();
