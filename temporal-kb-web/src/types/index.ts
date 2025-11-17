export interface Entry {
  id: number
  created_at: string
  updated_at: string
  entry_type: string
  title: string | null
  content: string
  word_count: number
  is_public: boolean
  tags: Tag[]
  projects: Project[]
}

export interface EntryCreate {
  entry_type: string
  title?: string
  content: string
  is_public?: boolean
  tag_ids?: number[]
  project_ids?: number[]
}

export interface EntryUpdate {
  entry_type?: string
  title?: string
  content?: string
  is_public?: boolean
  tag_ids?: number[]
  project_ids?: number[]
}

export interface Tag {
  id: number
  name: string
  description: string | null
}

export interface Project {
  id: number
  name: string
  description: string | null
}

export interface SearchResult {
  id: number
  title: string | null
  content: string
  entry_type: string
  created_at: string
  score: number
  excerpt?: string
}

export interface Link {
  id: number
  from_entry_id: number
  to_entry_id: number
  link_type: string
  strength: number
  is_automatic: boolean
  to_entry?: Entry
  from_entry?: Entry
}

export interface TemporalEvent {
  id: number
  entry_id: number
  event_date: string
  event_type: string
  description: string | null
  entry?: Entry
}

export interface Stats {
  total_entries: number
  total_words: number
  entries_this_month: number
  entries_this_week: number
  avg_entry_length: number
  total_tags: number
  total_projects: number
}

export interface Config {
  apiBaseUrl: string
}
