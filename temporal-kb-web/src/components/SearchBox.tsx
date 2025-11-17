import { useState, FormEvent } from 'react'
import './SearchBox.css'

interface SearchBoxProps {
  onSearch: (query: string, searchType: 'keyword' | 'semantic' | 'hybrid') => void
  placeholder?: string
  autoFocus?: boolean
}

export default function SearchBox({
  onSearch,
  placeholder = 'Search entries...',
  autoFocus = false
}: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState<'keyword' | 'semantic' | 'hybrid'>('hybrid')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query, searchType)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="search-box">
      <div className="search-input-group">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="search-input"
          autoFocus={autoFocus}
        />
        <select
          value={searchType}
          onChange={(e) => setSearchType(e.target.value as 'keyword' | 'semantic' | 'hybrid')}
          className="search-type"
        >
          <option value="hybrid">Hybrid</option>
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
        </select>
        <button type="submit" className="search-button">
          Search
        </button>
      </div>
    </form>
  )
}
