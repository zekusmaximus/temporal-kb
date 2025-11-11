# Temporal Knowledge Base

A personal knowledge management system with temporal intelligence, semantic search, and automatic relationship detection.

## Features

- 📝 **Entry Management**: Create, edit, version, and organize knowledge entries
- 🔍 **Advanced Search**: Full-text, semantic, and hybrid search capabilities
- 🔗 **Automatic Linking**: AI-powered relationship detection between entries
- ⏰ **Temporal Intelligence**: "Then vs Now" comparisons, cyclical pattern detection
- 📊 **Knowledge Graph**: Visualize connections and find clusters
- 🏷️ **Smart Organization**: Tags, projects, and automatic categorization
- 📱 **API-First**: RESTful API for mobile/web clients
- 🔐 **Privacy-Focused**: Self-hosted, encrypted, Git-backed

## Architecture

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL (or SQLite for local)
- **Vector Search**: ChromaDB with sentence-transformers
- **CLI**: Click + Rich for terminal interface
- **API**: REST API with OpenAPI documentation

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/temporal-kb.git
cd temporal-kb

# Install with pip
pip install -e .

# Or with Poetry
poetry install

# Initialize database
kb init
```

### Usage
```bash
# Create an entry
kb add -t "My First Note" -e

# Search
kb search "digital consciousness"
kb search --semantic "Buddhist concepts"

# View recent entries
kb search --recent 10

# Start API server
kb serve
```

## Documentation

- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli-reference.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Architecture Overview](docs/architecture.md)

## Development
```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black kb/
ruff check kb/

# Type checking
mypy kb/
```

## Deployment

See [Deployment Guide](docs/deployment.md) for:
- VPS deployment (Hetzner, DigitalOcean, etc.)
- Docker deployment
- Local-first setup with Tailscale

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE)

## Author

Jeffrey - [GitHub](https://github.com/yourusername)