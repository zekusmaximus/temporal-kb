import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../api/client'
import type { Entry } from '../types'
import './EntryPage.css'

export default function EntryPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [entry, setEntry] = useState<Entry | null>(null)
  const [relatedEntries, setRelatedEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadEntry(parseInt(id))
    }
  }, [id])

  const loadEntry = async (entryId: number) => {
    try {
      setLoading(true)
      const [entryData, related] = await Promise.all([
        api.getEntry(entryId),
        api.getRelatedEntries(entryId, 5),
      ])
      setEntry(entryData)
      setRelatedEntries(related)
    } catch (err) {
      setError('Failed to load entry.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!entry || !confirm('Are you sure you want to delete this entry?')) {
      return
    }

    try {
      await api.deleteEntry(entry.id)
      navigate('/')
    } catch (err) {
      alert('Failed to delete entry.')
      console.error(err)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (error || !entry) {
    return (
      <div className="error">
        <strong>Error:</strong> {error || 'Entry not found'}
      </div>
    )
  }

  const title = entry.title || `Untitled ${entry.entry_type}`
  const contentHtml = DOMPurify.sanitize(marked(entry.content) as string)

  return (
    <div>
      <article className="entry-page">
        <header className="entry-header">
          <h1>{title}</h1>
          <div className="entry-metadata">
            <span>Type: {entry.entry_type}</span>
            <span className="separator">•</span>
            <span>Created: {format(new Date(entry.created_at), 'MMMM d, yyyy')}</span>
            <span className="separator">•</span>
            <span>{entry.word_count} words</span>
          </div>
          {(entry.tags.length > 0 || entry.projects.length > 0) && (
            <div className="entry-tags">
              {entry.tags.map((tag) => (
                <span key={tag.id} className="tag">
                  {tag.name}
                </span>
              ))}
              {entry.projects.map((project) => (
                <span key={project.id} className="project-tag">
                  {project.name}
                </span>
              ))}
            </div>
          )}
        </header>

        <div
          className="entry-content"
          dangerouslySetInnerHTML={{ __html: contentHtml }}
        />

        <footer className="entry-actions">
          <Link to={`/edit/${entry.id}`}>
            <button>Edit</button>
          </Link>
          <button onClick={handleDelete} style={{ marginLeft: '0.5em' }}>
            Delete
          </button>
        </footer>
      </article>

      {relatedEntries.length > 0 && (
        <aside className="related-section">
          <h2>Related Entries</h2>
          <ul className="related-list">
            {relatedEntries.map((related) => (
              <li key={related.id}>
                <Link to={`/entry/${related.id}`}>
                  {related.title || `Untitled ${related.entry_type}`}
                </Link>
                <span className="text-muted text-small">
                  {' '}
                  — {format(new Date(related.created_at), 'MMM d, yyyy')}
                </span>
              </li>
            ))}
          </ul>
        </aside>
      )}
    </div>
  )
}
