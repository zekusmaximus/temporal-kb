import { useState, useEffect, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import type { Tag, Project } from '../types'
import './EntryForm.css'

export default function CreateEntryPage() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [entryType, setEntryType] = useState('note')
  const [isPublic, setIsPublic] = useState(false)
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [selectedProjects, setSelectedProjects] = useState<number[]>([])
  const [availableTags, setAvailableTags] = useState<Tag[]>([])
  const [availableProjects, setAvailableProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMetadata()
  }, [])

  const loadMetadata = async () => {
    try {
      const [tags, projects] = await Promise.all([
        api.getTags(),
        api.getProjects(),
      ])
      setAvailableTags(tags)
      setAvailableProjects(projects)
    } catch (err) {
      console.error('Failed to load metadata:', err)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!content.trim()) {
      setError('Content is required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const entry = await api.createEntry({
        title: title.trim() || undefined,
        content: content.trim(),
        entry_type: entryType,
        is_public: isPublic,
        tag_ids: selectedTags.length > 0 ? selectedTags : undefined,
        project_ids: selectedProjects.length > 0 ? selectedProjects : undefined,
      })
      navigate(`/entry/${entry.id}`)
    } catch (err) {
      setError('Failed to create entry. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Create New Entry</h1>

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
            autoFocus
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
          <button type="submit" className="primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Entry'}
          </button>
          <button
            type="button"
            onClick={() => navigate(-1)}
            style={{ marginLeft: '0.5em' }}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
