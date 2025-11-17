import { useState } from 'react'
import api from '../api/client'
import SearchBox from '../components/SearchBox'
import EntryCard from '../components/EntryCard'
import type { SearchResult } from '../types'

export default function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (
    query: string,
    searchType: 'keyword' | 'semantic' | 'hybrid'
  ) => {
    try {
      setLoading(true)
      setError(null)
      setHasSearched(true)
      const data = await api.searchEntries(query, searchType, 50)
      setResults(data)
    } catch (err) {
      setError('Search failed. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Search</h1>

      <SearchBox onSearch={handleSearch} autoFocus />

      <div className="info">
        <p>
          <strong>Search modes:</strong>
        </p>
        <ul>
          <li><strong>Hybrid</strong> - Combines keyword and semantic search for best results</li>
          <li><strong>Keyword</strong> - Traditional full-text search for exact matches</li>
          <li><strong>Semantic</strong> - AI-powered search that understands meaning and context</li>
        </ul>
      </div>

      {loading && <div className="loading">Searching...</div>}

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {!loading && hasSearched && (
        <section className="section">
          <h2>
            Results {results.length > 0 && `(${results.length})`}
          </h2>
          {results.length > 0 ? (
            <div>
              {results.map((result) => (
                <EntryCard key={result.id} entry={result} showExcerpt />
              ))}
            </div>
          ) : (
            <p>No results found. Try a different search query or mode.</p>
          )}
        </section>
      )}
    </div>
  )
}
