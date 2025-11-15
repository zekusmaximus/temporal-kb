export interface Entry {
  id: string;
  title: string;
  content: string;
  entry_type: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  projects: string[];
  word_count: number;
  version_count?: number;
}

export interface EntryCreate {
  title: string;
  content: string;
  entry_type: string;
  tags?: string[];
  projects?: string[];
}

export interface SearchParams {
  q?: string;
  tags?: string[];
  projects?: string[];
  entry_types?: string[];
  limit?: number;
}

export interface ApiConfig {
  baseUrl: string;
  apiKey: string;
}

export interface SemanticSearchResult {
  entry: Entry;
  similarity_score: number;
}

export interface RelatedEntry {
  entry: Entry;
  relevance_score: number;
}
