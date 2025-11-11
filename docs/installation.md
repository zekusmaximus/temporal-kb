# Installation Guide

## Requirements

- Python 3.10 or higher
- PostgreSQL 14+ (or SQLite for local use)
- 2GB RAM minimum
- 10GB disk space

## Local Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/temporal-kb.git
cd temporal-kb
```

### 2. Install Python Dependencies

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

**Using Poetry:**
```bash
poetry install
poetry shell
```

### 3. Initialize Database
```bash
# SQLite (simplest for local use)
kb init

# PostgreSQL (for production)
export KB_POSTGRES_URL="postgresql://user:pass@localhost:5432/temporal_kb"
kb init
```

### 4. Verify Installation
```bash
kb --help
kb info
```

## Server Installation

See [Deployment Guide](deployment.md) for VPS setup.