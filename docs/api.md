# API Documentation

The Temporal Knowledge Base API is a RESTful API built with FastAPI, providing programmatic access to all knowledge management features.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API supports API key authentication. Include your API key in the header:

```bash
Authorization: Bearer YOUR_API_KEY
```

Configure API keys in your config file or via environment variable:
```bash
export KB_API_KEYS='["your-secret-key-here"]'
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Core Endpoints

### System

#### Health Check
```http
GET /health
```

Returns the API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T10:30:00",
  "version": "0.1.0"
}
```

---

## Entries API

### Create Entry
```http
POST /api/v1/entries
```

Create a new knowledge base entry.

**Request Body:**
```json
{
  "title": "My Note Title",
  "content": "The note content in markdown format...",
  "entry_type": "note",
  "source": "manual",
  "tags": ["tag1", "tag2"],
  "projects": ["project-name"]
}
```

**Entry Types**: `note`, `journal`, `article`, `snippet`, `bookmark`, `task`

**Response:** `201 Created`
```json
{
  "id": "ent_a1b2c3d4e5f6",
  "created_at": "2025-11-12T10:30:00",
  "updated_at": "2025-11-12T10:30:00",
  "entry_type": "note",
  "title": "My Note Title",
  "content": "The note content...",
  "word_count": 245,
  "tags": ["tag1", "tag2"],
  "projects": ["project-name"],
  "version_count": 1
}
```

### Get Entry
```http
GET /api/v1/entries/{entry_id}
```

Retrieve a specific entry by ID.

**Response:** `200 OK`

### List Entries
```http
GET /api/v1/entries?limit=20&offset=0&entry_type=note
```

List entries with pagination and filtering.

**Query Parameters:**
- `limit` (int): Number of entries to return (default: 20, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `entry_type` (string): Filter by entry type
- `tag` (string): Filter by tag
- `project` (string): Filter by project

**Response:** `200 OK`
```json
{
  "entries": [...],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### Update Entry
```http
PUT /api/v1/entries/{entry_id}
PATCH /api/v1/entries/{entry_id}
```

Update an entry. Creates a new version automatically.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "tags": ["tag1", "tag3"]
}
```

**Response:** `200 OK`

### Delete Entry
```http
DELETE /api/v1/entries/{entry_id}
```

Delete an entry (soft delete - can be recovered).

**Query Parameters:**
- `permanent` (bool): If true, permanently delete (default: false)

**Response:** `204 No Content`

### Get Entry Versions
```http
GET /api/v1/entries/{entry_id}/versions
```

Get all versions of an entry.

**Response:** `200 OK`
```json
[
  {
    "version_number": 2,
    "created_at": "2025-11-12T10:35:00",
    "title": "Updated Title",
    "content_hash": "abc123...",
    "word_count": 250
  },
  {
    "version_number": 1,
    "created_at": "2025-11-12T10:30:00",
    "title": "Original Title",
    "content_hash": "def456...",
    "word_count": 245
  }
]
```

---

## Search API

### Full-Text Search
```http
GET /api/v1/search?q=query&mode=fts
```

Search entries using various methods.

**Query Parameters:**
- `q` (string, required): Search query
- `mode` (string): Search mode - `fts` (full-text), `semantic`, `hybrid` (default: fts)
- `limit` (int): Maximum results (default: 20)
- `entry_type` (string): Filter by entry type
- `tags` (array): Filter by tags
- `date_from` (datetime): Filter entries after date
- `date_to` (datetime): Filter entries before date

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "ent_a1b2c3d4e5f6",
      "title": "Matching Entry",
      "snippet": "...highlighted text...",
      "score": 0.95,
      "created_at": "2025-11-12T10:30:00",
      "tags": ["tag1"],
      "entry_type": "note"
    }
  ],
  "total": 5,
  "query": "search query",
  "mode": "fts"
}
```

### Semantic Search
```http
GET /api/v1/search?q=conceptual+query&mode=semantic
```

AI-powered semantic search using vector embeddings.

### Hybrid Search
```http
GET /api/v1/search?q=query&mode=hybrid
```

Combines full-text and semantic search for best results.

---

## Links API

### Get Entry Links
```http
GET /api/v1/links/{entry_id}
```

Get all links for an entry (both outgoing and incoming).

**Response:** `200 OK`
```json
{
  "entry_id": "ent_a1b2c3d4e5f6",
  "outgoing_links": [
    {
      "target_id": "ent_x9y8z7w6v5u4",
      "link_type": "references",
      "strength": 0.85,
      "created_at": "2025-11-12T10:30:00"
    }
  ],
  "incoming_links": [...]
}
```

### Create Link
```http
POST /api/v1/links
```

Create a link between two entries.

**Request Body:**
```json
{
  "source_id": "ent_a1b2c3d4e5f6",
  "target_id": "ent_x9y8z7w6v5u4",
  "link_type": "references",
  "strength": 0.9
}
```

**Link Types**: `references`, `similar_to`, `related_to`, `inspired_by`, `contradicts`, `extends`

**Response:** `201 Created`

### Delete Link
```http
DELETE /api/v1/links/{source_id}/{target_id}
```

Delete a specific link.

**Response:** `204 No Content`

### Suggest Links
```http
POST /api/v1/links/suggest
```

AI-powered link suggestions for an entry.

**Request Body:**
```json
{
  "entry_id": "ent_a1b2c3d4e5f6",
  "limit": 10,
  "min_strength": 0.7
}
```

**Response:** `200 OK`
```json
{
  "suggestions": [
    {
      "target_id": "ent_x9y8z7w6v5u4",
      "target_title": "Related Entry",
      "link_type": "similar_to",
      "strength": 0.92,
      "reason": "Both discuss temporal reasoning"
    }
  ]
}
```

---

## Temporal API

### Then vs Now
```http
GET /api/v1/temporal/then-now?topic=topic&days_ago=30
```

Compare current thinking with past thoughts on a topic.

**Query Parameters:**
- `topic` (string): Topic to analyze
- `days_ago` (int): How far back to look (default: 30)

**Response:** `200 OK`
```json
{
  "topic": "artificial intelligence",
  "then": {
    "date_range": "2025-10-01 to 2025-10-15",
    "entries": [...],
    "summary": "Earlier thoughts focused on..."
  },
  "now": {
    "date_range": "2025-11-01 to 2025-11-12",
    "entries": [...],
    "summary": "Recent thoughts emphasize..."
  },
  "evolution": "Your thinking has evolved to include..."
}
```

### Time Series
```http
GET /api/v1/temporal/timeseries?topic=topic&interval=week
```

Get time-series data for a topic.

**Query Parameters:**
- `topic` (string): Topic to analyze
- `interval` (string): Time interval - `day`, `week`, `month` (default: week)
- `date_from` (datetime): Start date
- `date_to` (datetime): End date

**Response:** `200 OK`
```json
{
  "topic": "meditation",
  "interval": "week",
  "data_points": [
    {
      "period": "2025-W45",
      "entry_count": 5,
      "avg_word_count": 324,
      "sentiment": 0.75
    }
  ]
}
```

### Cyclical Patterns
```http
GET /api/v1/temporal/cycles?topic=topic
```

Detect cyclical patterns in entries.

**Response:** `200 OK`
```json
{
  "topic": "productivity",
  "patterns": [
    {
      "type": "weekly",
      "description": "Productivity peaks on Tuesdays",
      "confidence": 0.87
    },
    {
      "type": "monthly",
      "description": "Review entries cluster at month-end",
      "confidence": 0.92
    }
  ]
}
```

---

## Tags API

### List Tags
```http
GET /api/v1/tags
```

Get all tags with usage counts.

**Response:** `200 OK`
```json
[
  {
    "name": "productivity",
    "entry_count": 42,
    "created_at": "2025-10-01T10:00:00"
  },
  {
    "name": "research",
    "entry_count": 28,
    "created_at": "2025-10-05T15:30:00"
  }
]
```

### Get Tag Entries
```http
GET /api/v1/tags/{tag_name}/entries
```

Get all entries with a specific tag.

### Rename Tag
```http
PUT /api/v1/tags/{tag_name}
```

Rename a tag across all entries.

**Request Body:**
```json
{
  "new_name": "new-tag-name"
}
```

### Delete Tag
```http
DELETE /api/v1/tags/{tag_name}
```

Remove tag from all entries and delete it.

---

## Projects API

### List Projects
```http
GET /api/v1/projects
```

Get all projects with metadata.

### Create Project
```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "project-name",
  "description": "Project description",
  "metadata": {
    "status": "active",
    "priority": "high"
  }
}
```

### Get Project Entries
```http
GET /api/v1/projects/{project_name}/entries
```

Get all entries in a project.

---

## Statistics API

### Get Stats
```http
GET /api/v1/stats
```

Get overall knowledge base statistics.

**Response:** `200 OK`
```json
{
  "total_entries": 487,
  "total_words": 123456,
  "total_links": 892,
  "entry_types": {
    "note": 245,
    "journal": 180,
    "article": 42,
    "snippet": 20
  },
  "top_tags": [
    {"name": "productivity", "count": 42},
    {"name": "research", "count": 28}
  ],
  "recent_activity": [...]
}
```

---

## Export API

### Export Entries
```http
GET /api/v1/export?format=markdown&tag=productivity
```

Export entries in various formats.

**Query Parameters:**
- `format` (string): Export format - `markdown`, `json`, `html` (default: markdown)
- `tag` (string): Filter by tag
- `project` (string): Filter by project
- `date_from` (datetime): Filter by date range
- `date_to` (datetime): Filter by date range

**Response:** File download or JSON with export data

---

## Error Responses

All endpoints may return these error codes:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource or conflict
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. For production deployments, consider implementing rate limiting at the reverse proxy level.

---

## WebSocket Support

WebSocket endpoints for real-time updates are planned for future versions.

---

## Examples

### Python Client Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create entry
response = requests.post(
    f"{API_BASE}/entries",
    headers=headers,
    json={
        "title": "My Note",
        "content": "Note content...",
        "entry_type": "note",
        "tags": ["example"]
    }
)
entry = response.json()

# Search
response = requests.get(
    f"{API_BASE}/search",
    headers=headers,
    params={"q": "example query", "mode": "semantic"}
)
results = response.json()
```

### cURL Example

```bash
# Create entry
curl -X POST http://localhost:8000/api/v1/entries \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Note",
    "content": "Note content...",
    "entry_type": "note",
    "tags": ["example"]
  }'

# Search
curl -X GET "http://localhost:8000/api/v1/search?q=example&mode=semantic" \
  -H "Authorization: Bearer your-api-key"
```

---

## Version History

- **v0.1.0** (2025-11-12): Initial API release

---

For more information, see:
- [Installation Guide](installation.md)
- [CLI Reference](cli-reference.md)
- [Deployment Guide](deployment.md)
