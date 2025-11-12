# Contributing to Temporal Knowledge Base

Thank you for your interest in contributing to Temporal KB! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

This project follows a standard code of conduct:
- Be respectful and inclusive
- Welcome newcomers and beginners
- Focus on constructive feedback
- Assume good intentions

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/temporal-kb.git
   cd temporal-kb
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/temporal-kb.git
   ```

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Optional: PostgreSQL for database testing

### Install Development Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with dev dependencies
pip install -e ".[dev]"
```

### Verify Setup

```bash
# Run tests
pytest

# Check code formatting
black --check kb/
ruff check kb/

# Type checking
mypy kb/
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-x` - New features
- `fix/issue-123` - Bug fixes
- `docs/update-readme` - Documentation
- `refactor/improve-y` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `chore`: Maintenance tasks

**Examples:**
```
feat(search): add semantic search capability

Implemented vector-based semantic search using ChromaDB
and sentence-transformers. Allows conceptual queries
beyond keyword matching.

Closes #42
```

```
fix(cli): resolve circular import in importers

Moved ImporterBase to separate base.py module to break
circular dependency between import_service and importer classes.
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kb --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::TestEntry::test_create_entry
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested
- Include docstrings explaining the test purpose

**Example:**
```python
def test_create_entry_with_tags(self, entry_service):
    """Test that entries can be created with multiple tags"""
    entry_data = EntryCreate(
        title="Test",
        content="Content",
        tags=["tag1", "tag2"]
    )
    entry = entry_service.create_entry(entry_data)
    assert len(entry.tags) == 2
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters (enforced by black)
- Use type hints where appropriate
- Document all public functions and classes

### Formatting

```bash
# Auto-format code
black kb/

# Check imports
ruff check kb/ --fix

# Type checking
mypy kb/
```

### Documentation

- Use docstrings for all public modules, functions, classes, and methods
- Follow Google-style docstrings:

```python
def create_entry(self, data: EntryCreate) -> Entry:
    """
    Create a new knowledge base entry.
    
    Args:
        data: Entry creation data with title, content, etc.
    
    Returns:
        Created Entry object with generated ID
    
    Raises:
        ValueError: If title is empty or content is invalid
    """
    pass
```

## Pull Request Process

### Before Submitting

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   pytest
   black --check kb/
   ruff check kb/
   mypy kb/
   ```

3. **Update documentation** if needed

4. **Write/update tests** for your changes

### Submitting PR

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature
   ```

2. **Create Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes
   - List breaking changes if any

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

- At least one maintainer approval required
- CI checks must pass
- Address review feedback promptly
- Update PR description if scope changes

## Release Process

Maintainers follow semantic versioning (SemVer):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backwards compatible
- **Patch** (0.0.1): Bug fixes

## Areas for Contribution

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage improvements
- Small bug fixes
- Code cleanup

### Feature Requests

Before implementing large features:
1. Open an issue to discuss the feature
2. Get maintainer feedback
3. Agree on implementation approach
4. Submit PR

### Documentation

Documentation contributions are always welcome:
- Improve existing docs
- Add examples and tutorials
- Fix typos and clarify confusing sections
- Add API documentation

## Getting Help

- **Issues**: Open an issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Discord**: [Link to Discord] (if available)

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in documentation where appropriate

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Temporal Knowledge Base! 🎉
