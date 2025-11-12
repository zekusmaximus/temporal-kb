#!/bin/bash

# Temporal KB Backup Script
# Creates a complete backup of the knowledge base

set -e  # Exit on error

# Configuration
DATA_DIR="${KB_DATA_DIR:-$HOME/.temporal-kb/data}"
BACKUP_DIR="${KB_BACKUP_DIR:-$HOME/.temporal-kb/backups}"
RETENTION_DAYS="${KB_BACKUP_RETENTION:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kb_backup_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "====================================="
echo "Temporal KB Backup Script"
echo "====================================="
echo ""
echo "Data directory: $DATA_DIR"
echo "Backup directory: $BACKUP_DIR"
echo "Backup name: $BACKUP_NAME"
echo ""

# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Data directory not found: $DATA_DIR"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create temporary backup directory
mkdir -p "$BACKUP_PATH"

echo "Creating backup..."

# Backup database
if [ -f "$DATA_DIR/db/kb.db" ]; then
    echo "  → Backing up SQLite database..."
    mkdir -p "$BACKUP_PATH/db"
    cp "$DATA_DIR/db/kb.db" "$BACKUP_PATH/db/"
fi

# Backup entries
if [ -d "$DATA_DIR/entries" ]; then
    echo "  → Backing up entry files..."
    cp -r "$DATA_DIR/entries" "$BACKUP_PATH/"
fi

# Backup vector database
if [ -d "$DATA_DIR/vectors" ]; then
    echo "  → Backing up vector database..."
    cp -r "$DATA_DIR/vectors" "$BACKUP_PATH/"
fi

# Backup configuration
if [ -d "$HOME/.temporal-kb/config" ]; then
    echo "  → Backing up configuration..."
    cp -r "$HOME/.temporal-kb/config" "$BACKUP_PATH/"
fi

# Create backup metadata
cat > "$BACKUP_PATH/metadata.txt" << EOF
Temporal KB Backup
==================

Backup date: $(date)
Hostname: $(hostname)
Data directory: $DATA_DIR

Contents:
$(du -sh "$BACKUP_PATH"/* 2>/dev/null | sed 's/^/  /')

EOF

# Compress backup
echo "Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Calculate size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo "✓ Backup created: ${BACKUP_NAME}.tar.gz"
echo "  Size: $BACKUP_SIZE"
echo "  Location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# Clean up old backups
if [ "$RETENTION_DAYS" -gt 0 ]; then
    echo ""
    echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    find "$BACKUP_DIR" -name "kb_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    REMAINING=$(ls -1 "$BACKUP_DIR"/kb_backup_*.tar.gz 2>/dev/null | wc -l)
    echo "  Backups remaining: $REMAINING"
fi

echo ""
echo "====================================="
echo "Backup completed successfully!"
echo "====================================="
echo ""

# Optional: Upload to remote storage
if [ -n "$KB_BACKUP_REMOTE" ]; then
    echo "Uploading to remote storage: $KB_BACKUP_REMOTE"
    # Example with rsync:
    # rsync -avz "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" "$KB_BACKUP_REMOTE/"
    # Example with S3:
    # aws s3 cp "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" "s3://your-bucket/backups/"
fi

# Exit successfully
exit 0
