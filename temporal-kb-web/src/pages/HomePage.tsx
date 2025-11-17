import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import EntryCard from '../components/EntryCard'
import type { Entry, Stats } from '../types'

export default function HomePage() {
  const [recentEntries, setRecentEntries] = useState<Entry[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [entries, statsData] = await Promise.all([
        api.getRecentEntries(10),
        api.getStats(),
      ])
      setRecentEntries(entries)
      setStats(statsData)
    } catch (err) {
      setError('Failed to load data. Please ensure the API server is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (error) {
    return (
      <div className="error">
        <strong>Error:</strong> {error}
      </div>
    )
  }

  return (
    <div>
      <h1>Welcome to Your Knowledge Base</h1>

      <div className="info" style={{ marginTop: '1em' }}>
        <p>
          A personal knowledge management system with temporal intelligence and
          AI-powered semantic search.
        </p>
      </div>

      {stats && (
        <section className="section">
          <h2>Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1em' }}>
            <div>
              <div className="text-muted">Total Entries</div>
              <div style={{ fontSize: '1.5em' }}>{stats.total_entries}</div>
            </div>
            <div>
              <div className="text-muted">Total Words</div>
              <div style={{ fontSize: '1.5em' }}>{stats.total_words.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-muted">This Week</div>
              <div style={{ fontSize: '1.5em' }}>{stats.entries_this_week}</div>
            </div>
            <div>
              <div className="text-muted">This Month</div>
              <div style={{ fontSize: '1.5em' }}>{stats.entries_this_month}</div>
            </div>
          </div>
        </section>
      )}

      <section className="section">
        <h2>Recent Entries</h2>
        {recentEntries.length > 0 ? (
          <div>
            {recentEntries.map((entry) => (
              <EntryCard key={entry.id} entry={entry} />
            ))}
          </div>
        ) : (
          <p>
            No entries yet. <Link to="/create">Create your first entry</Link>
          </p>
        )}
      </section>

      <section className="section">
        <h2>Quick Links</h2>
        <ul>
          <li>
            <Link to="/search">Search your knowledge base</Link>
          </li>
          <li>
            <Link to="/timeline">View timeline of events</Link>
          </li>
          <li>
            <Link to="/discover">Discover connections</Link>
          </li>
          <li>
            <Link to="/create">Create a new entry</Link>
          </li>
        </ul>
      </section>
    </div>
  )
}
