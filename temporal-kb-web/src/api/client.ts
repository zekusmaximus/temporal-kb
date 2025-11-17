import axios, { AxiosInstance } from 'axios'
import type {
  Entry,
  EntryCreate,
  EntryUpdate,
  SearchResult,
  Link,
  Tag,
  Project,
  TemporalEvent,
  Stats,
} from '../types'

class ApiClient {
  private client: AxiosInstance

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // Entries
  async getEntries(
    skip: number = 0,
    limit: number = 50
  ): Promise<Entry[]> {
    const response = await this.client.get('/entries', {
      params: { skip, limit },
    })
    return response.data
  }

  async getEntry(id: number): Promise<Entry> {
    const response = await this.client.get(`/entries/${id}`)
    return response.data
  }

  async createEntry(entry: EntryCreate): Promise<Entry> {
    const response = await this.client.post('/entries', entry)
    return response.data
  }

  async updateEntry(id: number, entry: EntryUpdate): Promise<Entry> {
    const response = await this.client.put(`/entries/${id}`, entry)
    return response.data
  }

  async deleteEntry(id: number): Promise<void> {
    await this.client.delete(`/entries/${id}`)
  }

  async getRecentEntries(limit: number = 10): Promise<Entry[]> {
    const response = await this.client.get('/search/recent', {
      params: { limit },
    })
    return response.data
  }

  // Search
  async searchEntries(
    query: string,
    search_type: 'keyword' | 'semantic' | 'hybrid' = 'hybrid',
    limit: number = 20
  ): Promise<SearchResult[]> {
    const response = await this.client.get('/search', {
      params: { q: query, search_type, limit },
    })
    return response.data
  }

  // Links
  async getEntryLinks(entryId: number): Promise<Link[]> {
    const response = await this.client.get(`/links/entry/${entryId}`)
    return response.data
  }

  async getRelatedEntries(entryId: number, limit: number = 10): Promise<Entry[]> {
    const response = await this.client.get(`/links/related/${entryId}`, {
      params: { limit },
    })
    return response.data
  }

  // Tags
  async getTags(): Promise<Tag[]> {
    const response = await this.client.get('/tags')
    return response.data
  }

  async createTag(name: string, description?: string): Promise<Tag> {
    const response = await this.client.post('/tags', { name, description })
    return response.data
  }

  async getEntriesByTag(tagId: number): Promise<Entry[]> {
    const response = await this.client.get(`/tags/${tagId}/entries`)
    return response.data
  }

  // Projects
  async getProjects(): Promise<Project[]> {
    const response = await this.client.get('/projects')
    return response.data
  }

  async createProject(name: string, description?: string): Promise<Project> {
    const response = await this.client.post('/projects', { name, description })
    return response.data
  }

  async getEntriesByProject(projectId: number): Promise<Entry[]> {
    const response = await this.client.get(`/projects/${projectId}/entries`)
    return response.data
  }

  // Temporal
  async getOnThisDay(
    month: number,
    day: number,
    years_back: number = 10
  ): Promise<TemporalEvent[]> {
    const response = await this.client.get('/temporal/on-this-day', {
      params: { month, day, years_back },
    })
    return response.data
  }

  async getTimeline(
    start_date?: string,
    end_date?: string
  ): Promise<TemporalEvent[]> {
    const response = await this.client.get('/temporal/timeline', {
      params: { start_date, end_date },
    })
    return response.data
  }

  // Stats
  async getStats(): Promise<Stats> {
    const response = await this.client.get('/stats')
    return response.data
  }
}

export const api = new ApiClient()
export default api
