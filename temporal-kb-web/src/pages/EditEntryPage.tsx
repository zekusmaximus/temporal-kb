import { useState, useEffect, FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import type { Entry, Tag, Project } from '../types'
import './EntryForm.css'

export default function EditEntryPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [entry, setEntry] = useState<Entry | null>(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [entryType, setEntryType] = useState('note')
  const [isPublic, setIsPublic] = useState(false)
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [selectedProjects, setSelectedProjects] = useState<number[]>([])
  const [availableTags, setAvailableTags] = useState<Tag[]>([])
  const [availableProjects, setAvailableProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadEntry(parseInt(id))
    }
  }, [id])

  const loadEntry = async (entryId: number) => {
    try {
      setLoading(true)
      const [entryData, tags, projects] = await Promise.all([
        api.getEntry(entryId),
        api.getTags(),
        api.getProjects(),
      ])
      setEntry(entryData)
      setTitle(entryData.title || '')
      setContent(entryData.content)
      setEntryType(entryData.entry_type)
      setIsPublic(entryData.is_public)
      setSelectedTags(entryData.tags.map((t) => t.id))
      setSelectedProjects(entryData.projects.map((p) => p.id))
      setAvailableTags(tags)
      setAvailableProjects(projects)
    } catch (err) {
      setError('Failed to load entry.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!entry || !content.trim()) {
      setError('Content is required')
      return
    }

    try {
      setSaving(true)
      setError(null)
      await api.updateEntry(entry.id, {
        title: title.trim() || undefined,
        content: content.trim(),
        entry_type: entryType,
        is_public: isPublic,
        tag_ids: selectedTags.length > 0 ? selectedTags : undefined,
        project_ids: selectedProjects.length > 0 ? selectedProjects : undefined,
      })
      navigate(`/entry/${entry.id}`)
    } catch (err) {
      setError('Failed to update entry. Please try again.')
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (error && !entry) {
    return (
      <div className="error">
        <strong>Error:</strong> {error}
      </div>
    )
  }

  return (
    <div>
      <h1>Edit Entry</h1>

      <form onSubmit={handleSubmit} className="entry-form">
        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="title">Title (optional)</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Entry title..."
          />
        </div>

        <div className="form-group">
          <label htmlFor="entry-type">Entry Type</label>
          <select
            id="entry-type"
            value={entryType}
            onChange={(e) => setEntryType(e.target.value)}
          >
            <option value="note">Note</option>
            <option value="journal">Journal</option>
            <option value="article">Article</option>
            <option value="idea">Idea</option>
            <option value="todo">Todo</option>
            <option value="snippet">Snippet</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="content">
            Content <span className="required">*</span>
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your entry here... (Markdown supported)"
            required
          />
          <div className="text-muted text-small">
            Markdown formatting is supported
          </div>
        </div>

        {availableTags.length > 0 && (
          <div className="form-group">
            <label>Tags</label>
            <div className="checkbox-group">
              {availableTags.map((tag) => (
                <label key={tag.id} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedTags.includes(tag.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedTags([...selectedTags, tag.id])
                      } else {
                        setSelectedTags(selectedTags.filter((id) => id !== tag.id))
                      }
                    }}
                  />
                  {tag.name}
                </label>
              ))}
            </div>
          </div>
        )}

        {availableProjects.length > 0 && (
          <div className="form-group">
            <label>Projects</label>
            <div className="checkbox-group">
              {availableProjects.map((project) => (
                <label key={project.id} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedProjects.includes(project.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedProjects([...selectedProjects, project.id])
                      } else {
                        setSelectedProjects(
                          selectedProjects.filter((id) => id !== project.id)
                        )
                      }
                    }}
                  />
                  {project.name}
                </label>
              ))}
            </div>
          </div>
        )}

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
            />
            Make this entry public
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" className="primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => navigate(`/entry/${entry?.id}`)}
            style={{ marginLeft: '0.5em' }}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
