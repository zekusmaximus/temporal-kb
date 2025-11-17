import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import type { Entry, Link as EntryLink } from '../types'
import './DiscoverPage.css'

export default function DiscoverPage() {
  const [entryId, setEntryId] = useState('')
  const [entry, setEntry] = useState<Entry | null>(null)
  const [links, setLinks] = useState<EntryLink[]>([])
  const [related, setRelated] = useState<Entry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDiscover = async () => {
    const id = parseInt(entryId)
    if (isNaN(id)) {
      setError('Please enter a valid entry ID')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const [entryData, linksData, relatedData] = await Promise.all([
        api.getEntry(id),
        api.getEntryLinks(id),
        api.getRelatedEntries(id, 20),
      ])
      setEntry(entryData)
      setLinks(linksData)
      setRelated(relatedData)
    } catch (err) {
      setError('Failed to load entry relationships.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Discover Connections</h1>

      <div className="info">
        <p>
          Explore the relationships between entries. The system automatically
          detects semantic connections and explicit links between your knowledge
          base entries.
        </p>
      </div>

      <div className="discover-form">
        <label htmlFor="entry-id">Entry ID to explore:</label>
        <div style={{ display: 'flex', gap: '0.5em', marginTop: '0.5em' }}>
          <input
            id="entry-id"
            type="number"
            value={entryId}
            onChange={(e) => setEntryId(e.target.value)}
            placeholder="Enter entry ID..."
            style={{ flex: 1 }}
          />
          <button onClick={handleDiscover} disabled={loading}>
            {loading ? 'Loading...' : 'Discover'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {entry && (
        <div className="discovery-results">
          <section className="section">
            <h2>Selected Entry</h2>
            <div className="selected-entry">
              <h3>
                <Link to={`/entry/${entry.id}`}>
                  {entry.title || `Untitled ${entry.entry_type}`}
                </Link>
              </h3>
              <p className="text-muted">
                {entry.entry_type} • {entry.word_count} words
              </p>
            </div>
          </section>

          {links.length > 0 && (
            <section className="section">
              <h2>Direct Links ({links.length})</h2>
              <div className="links-list">
                {links.map((link) => {
                  const linkedEntry =
                    link.from_entry_id === entry.id ? link.to_entry : link.from_entry
                  if (!linkedEntry) return null

                  return (
                    <div key={link.id} className="link-item">
                      <div className="link-info">
                        <span className={`link-badge ${link.is_automatic ? 'auto' : 'manual'}`}>
                          {link.is_automatic ? 'Auto' : 'Manual'}
                        </span>
                        <span className="link-type">{link.link_type}</span>
                        <span className="link-strength">
                          Strength: {(link.strength * 100).toFixed(0)}%
                        </span>
                      </div>
                      <Link to={`/entry/${linkedEntry.id}`} className="link-title">
                        {linkedEntry.title || `Untitled ${linkedEntry.entry_type}`}
                      </Link>
                    </div>
                  )
                })}
              </div>
            </section>
          )}

          {related.length > 0 && (
            <section className="section">
              <h2>Related Entries ({related.length})</h2>
              <p className="text-muted">
                Semantically similar entries based on content analysis
              </p>
              <div className="related-grid">
                {related.map((relatedEntry) => (
                  <div key={relatedEntry.id} className="related-card">
                    <h4>
                      <Link to={`/entry/${relatedEntry.id}`}>
                        {relatedEntry.title || `Untitled ${relatedEntry.entry_type}`}
                      </Link>
                    </h4>
                    <p className="text-muted text-small">
                      {relatedEntry.entry_type} • {relatedEntry.word_count} words
                    </p>
                    <p className="related-excerpt">
                      {relatedEntry.content.substring(0, 150)}...
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {links.length === 0 && related.length === 0 && (
            <div className="info">
              <p>No connections found for this entry yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
