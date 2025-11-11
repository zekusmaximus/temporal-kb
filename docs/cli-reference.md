# CLI Reference

Complete command-line interface reference for Temporal KB.

## Global Options
```bash
kb --config PATH      # Use custom config file
kb --data-dir PATH    # Override data directory
```

## Commands

### Entry Management

#### Create Entry
```bash
kb add                              # Interactive mode
kb add -t "Title" -e               # Open editor
kb add -q "Quick note"             # Quick note
kb add --template legal_case       # Use template
```

#### Search
```bash
kb search "query"                   # Keyword search
kb search "query" --semantic        # Semantic search
kb search "query" --hybrid          # Hybrid search
kb search --recent 10               # Recent entries
kb search --tag philosophy          # Filter by tag
```

#### View Entry
```bash
kb show ENTRY_ID                    # Show entry
kb show ENTRY_ID --history          # Version history
kb show ENTRY_ID --version 3        # Specific version
```

#### Edit Entry
```bash
kb edit ENTRY_ID                    # Open in editor
kb edit ENTRY_ID --title "New"      # Update title
kb edit ENTRY_ID --add-tag python   # Add tag
```

#### Delete Entry
```bash
kb delete ENTRY_ID                  # Delete (with confirmation)
kb delete ENTRY_ID --force          # Delete without confirmation
```

### Link Management
```bash
kb link create FROM_ID TO_ID        # Create link
kb link detect ENTRY_ID             # Detect potential links
kb link related ENTRY_ID            # Find related entries
kb link stats                       # Graph statistics
```

### Temporal Queries
```bash
kb temporal on-this-day             # Entries from this day
kb temporal range --start YYYY-MM-DD --end YYYY-MM-DD
kb temporal compare ...             # Compare time periods
kb temporal evolution "topic"       # Track topic evolution
kb temporal patterns                # Analyze patterns
```

### Import Data
```bash
kb import markdown PATH             # Import markdown files
kb import email --server ... --username ... --password ...
kb import browser auto --browser chrome
kb import chat PATH                 # Import chat exports
```

### API Server
```bash
kb serve                            # Start API server
kb serve --port 8080                # Custom port
kb serve --reload                   # Auto-reload (dev)
```

### Index Management
```bash
kb index rebuild                    # Rebuild vector index
kb index stats                      # Index statistics
kb index update --all               # Update all entries
```

## Configuration

Config file location: `~/.temporal-kb/config/config.yaml`

See `.env.example` for environment variables.