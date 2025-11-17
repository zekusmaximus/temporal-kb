import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import type { Entry, SearchResult } from '../types'
import './EntryCard.css'

interface EntryCardProps {
  entry: Entry | SearchResult
  showExcerpt?: boolean
}

export default function EntryCard({ entry, showExcerpt = true }: EntryCardProps) {
  const title = entry.title || `Untitled ${entry.entry_type}`
  const date = format(new Date(entry.created_at), 'MMMM d, yyyy')

  // Get excerpt - either from search result or truncate content
  const excerpt = 'excerpt' in entry && entry.excerpt
    ? entry.excerpt
    : entry.content.substring(0, 200) + (entry.content.length > 200 ? '...' : '')

  return (
    <article className="entry-card">
      <h3 className="entry-title">
        <Link to={`/entry/${entry.id}`}>{title}</Link>
      </h3>
      <div className="entry-meta">
        <span className="entry-date">{date}</span>
        <span className="separator">•</span>
        <span className="entry-type">{entry.entry_type}</span>
        {'score' in entry && entry.score !== undefined && (
          <>
            <span className="separator">•</span>
            <span className="entry-score">Relevance: {(entry.score * 100).toFixed(0)}%</span>
          </>
        )}
      </div>
      {showExcerpt && <p className="entry-excerpt">{excerpt}</p>}
    </article>
  )
}
