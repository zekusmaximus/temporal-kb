# Architecture Overview

## System Components
```
┌─────────────────────────────────────────────────────┐
│                   Client Layer                       │
├─────────────────┬─────────────────┬─────────────────┤
│   CLI (Click)   │  Mobile (RN)    │  Web (React)    │
└────────┬────────┴────────┬────────┴────────┬────────┘
         │                 │                 │
         │                 └─────────┬───────┘
         │                           │
         │                    ┌──────▼──────┐
         │                    │  REST API   │
         │                    │  (FastAPI)  │
         │                    └──────┬──────┘
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │    Service Layer       │
         ├────────────────────────┤
         │  • EntryService        │
         │  • SearchService       │
         │  • LinkService         │
         │  • TemporalService     │
         │  • ImportService       │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   Storage Layer        │
         ├────────────────────────┤
         │  • PostgreSQL/SQLite   │
         │  • ChromaDB (vectors)  │
         │  • File System         │
         │  • Git Repository      │
         └────────────────────────┘
```

## Data Flow

### Entry Creation
1. User creates entry via CLI/API
2. EntryService validates & processes
3. Content saved to database
4. File written to file system
5. Embedding generated (async)
6. Git commit (optional)
7. Links auto-detected

### Search Flow
1. User queries via CLI/API
2. SearchService determines search type
3. Full-text search (PostgreSQL/SQLite FTS)
4. Semantic search (ChromaDB vectors)
5. Results merged & ranked
6. Return to user

## Key Design Decisions

### SQLAlchemy ORM
- Portable across SQLite/PostgreSQL
- Type-safe queries
- Automatic migrations

### ChromaDB for Vectors
- Local-first (no cloud required)
- Persistent storage
- Fast similarity search

### Git for Version Control
- Human-readable diffs
- Distributed backups
- Easy rollback

### FastAPI for REST API
- Auto-generated docs
- Type validation
- Async support
- Fast performance

## Database Schema

See [models.py](../kb/core/models.py) for complete schema.

Key tables:
- `entries` - Main content
- `entry_versions` - Version history
- `entry_links` - Relationships
- `tags` - Organization
- `projects` - Grouping