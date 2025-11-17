import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import api from '../api/client'
import type { TemporalEvent } from '../types'
import './TimelinePage.css'

export default function TimelinePage() {
  const [events, setEvents] = useState<TemporalEvent[]>([])
  const [onThisDayEvents, setOnThisDayEvents] = useState<TemporalEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTimeline()
  }, [])

  const loadTimeline = async () => {
    try {
      setLoading(true)
      const now = new Date()
      const [timelineData, onThisDay] = await Promise.all([
        api.getTimeline(),
        api.getOnThisDay(now.getMonth() + 1, now.getDate(), 10),
      ])
      setEvents(timelineData)
      setOnThisDayEvents(onThisDay)
    } catch (err) {
      setError('Failed to load timeline.')
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

  const today = new Date()
  const todayFormatted = format(today, 'MMMM d')

  return (
    <div>
      <h1>Timeline</h1>

      {onThisDayEvents.length > 0 && (
        <section className="section on-this-day">
          <h2>On This Day ({todayFormatted})</h2>
          <p className="text-muted">
            Events and entries from {todayFormatted} in previous years
          </p>
          <div className="timeline">
            {onThisDayEvents.map((event) => (
              <div key={event.id} className="timeline-item">
                <div className="timeline-date">
                  {format(new Date(event.event_date), 'yyyy')}
                </div>
                <div className="timeline-content">
                  <div className="event-type">{event.event_type}</div>
                  {event.description && <p>{event.description}</p>}
                  {event.entry && (
                    <Link to={`/entry/${event.entry.id}`}>
                      {event.entry.title || `Untitled ${event.entry.entry_type}`}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="section">
        <h2>All Events</h2>
        {events.length > 0 ? (
          <div className="timeline">
            {events.map((event) => (
              <div key={event.id} className="timeline-item">
                <div className="timeline-date">
                  {format(new Date(event.event_date), 'MMM d, yyyy')}
                </div>
                <div className="timeline-content">
                  <div className="event-type">{event.event_type}</div>
                  {event.description && <p>{event.description}</p>}
                  {event.entry && (
                    <Link to={`/entry/${event.entry.id}`}>
                      {event.entry.title || `Untitled ${event.entry.entry_type}`}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No temporal events found. Events are created automatically when you add entries.</p>
        )}
      </section>
    </div>
  )
}
