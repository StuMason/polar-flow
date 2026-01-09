# Contributing to polar-flow

Thank you for your interest in contributing! This document outlines the process and standards for contributing to polar-flow.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) installed
- Git
- A Polar AccessLink API account ([register here](https://admin.polaraccesslink.com))

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/polar-flow.git
   cd polar-flow
   ```

2. Install dependencies:
   ```bash
   uv sync --dev
   ```

3. Set up pre-commit hooks (optional but recommended):
   ```bash
   uv run pre-commit install
   ```

4. Run tests to verify setup:
   ```bash
   uv run pytest
   ```

## Development Workflow

### Branch Strategy

- **main** - Production-ready code, protected branch
- **feat/*** - Feature branches (e.g., `feat/add-sleep-endpoint`)
- **fix/*** - Bug fix branches (e.g., `fix/rate-limit-handling`)
- **chore/*** - Maintenance tasks (e.g., `chore/update-dependencies`)

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. Make your changes following our [Code Standards](#code-standards)

3. Run tests and linting:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run ruff format .
   uv run mypy src/polar_flow
   ```

4. Commit with descriptive messages:
   ```bash
   git commit -m "feat: add sleep endpoint with full type coverage"
   ```

5. Push to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```

6. Create a Pull Request on GitHub

## Code Standards

### Python Style

- **Python version**: 3.11+ (use modern syntax)
- **Line length**: 100 characters
- **Formatting**: Ruff (runs automatically in pre-commit)
- **Linting**: Ruff with strict rules
- **Type checking**: mypy in strict mode (MUST pass with zero errors)

### Type Hints (MANDATORY)

ALL functions must have complete type hints:

```python
# ✅ Good
async def get_sleep(self, date: str) -> SleepData:
    """Fetch sleep data for a specific date."""
    ...

# ❌ Bad - missing type hints
async def get_sleep(self, date):
    ...
```

Use modern syntax:
- `str | None` NOT `Optional[str]`
- `list[str]` NOT `List[str]`
- `dict[str, int]` NOT `Dict[str, int]`

### Imports

Group and sort imports:

```python
# 1. Standard library
import asyncio
from datetime import date

# 2. Third-party
import httpx
from pydantic import BaseModel, Field

# 3. Local
from polar_flow.exceptions import NotFoundError
```

### Async/Await

- Primary API is async-first
- Use `async with` for context managers
- Use `httpx` for HTTP requests (NOT `requests`)

### Pydantic Models

- Use Pydantic 2.x syntax
- Add field descriptions and validation
- Include docstrings
- Add computed properties for derived values

```python
from pydantic import BaseModel, Field

class SleepData(BaseModel):
    """Sleep tracking data for a single night."""

    sleep_score: int = Field(ge=0, le=100, description="Overall sleep quality score")
    light_sleep: int = Field(description="Light sleep duration in seconds")

    @property
    def total_sleep_hours(self) -> float:
        """Total sleep time in hours."""
        return self.light_sleep / 3600
```

### Error Handling

- Never raise generic `Exception`
- Use typed custom exceptions from `exceptions.py`
- Include helpful error messages with context

```python
# ✅ Good
raise NotFoundError(f"Sleep data not found for date: {date}")

# ❌ Bad
raise Exception("Not found")
```

### Documentation

All public functions/classes need docstrings (Google style):

```python
async def get_sleep(self, date: str) -> SleepData:
    """Fetch sleep data for a specific date.

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        Sleep data for the specified date

    Raises:
        NotFoundError: If no sleep data exists for the date
        AuthenticationError: If access token is invalid
    """
```

## Testing Requirements

### Coverage Requirements

- **Minimum**: 80% code coverage (enforced by codecov)
- All new features must include tests
- All bug fixes must include regression tests

### Testing Tools

- **Framework**: pytest
- **Async testing**: pytest-asyncio
- **HTTP mocking**: pytest-httpx
- **Coverage**: pytest-cov

### Writing Tests

Follow the AAA pattern (Arrange, Act, Assert):

```python
async def test_get_sleep_success(httpx_mock):
    # Arrange
    httpx_mock.add_response(
        url="https://www.polaraccesslink.com/v3/users/123/sleep/2026-01-09",
        json={"sleep_score": 85, "light_sleep": 3600}
    )
    client = PolarFlow(access_token="test_token")

    # Act
    sleep = await client.sleep.get(user_id="123", date="2026-01-09")

    # Assert
    assert sleep.sleep_score == 85
    assert sleep.light_sleep == 3600
```

### Running Tests

```bash
# All tests with coverage
uv run pytest

# Specific test file
uv run pytest tests/test_exceptions.py

# Verbose output
uv run pytest -v

# Watch mode (requires pytest-watch)
uv run pytest-watch
```

## Documentation

### README Updates

If adding a new feature, update the README.md with:
- Feature description
- Code example
- Any new dependencies

### CHANGELOG

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [Unreleased]

### Added
- Sleep endpoint with full type coverage

### Fixed
- Rate limit error handling now includes retry_after header
```

### CLAUDE.md

If changing project structure or adding new patterns, update CLAUDE.md.

## Submitting Changes

### Pull Request Process

1. Ensure all tests pass:
   ```bash
   uv run pytest
   uv run mypy src/polar_flow
   uv run ruff check .
   ```

2. Update documentation:
   - README.md if adding features
   - CHANGELOG.md with your changes
   - Docstrings for all new code

3. Create a Pull Request with:
   - Clear title describing the change
   - Description explaining what and why
   - Link to related issues (if applicable)

4. Wait for CI checks to pass:
   - Tests (Python 3.11, 3.12, 3.13)
   - Linting (Ruff)
   - Type checking (mypy)
   - Coverage (80%+ required)

5. Address review feedback if requested

6. Once approved, a maintainer will merge your PR

### Commit Message Format

Use conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks
- `refactor:` - Code refactoring

Examples:
```
feat: add nightly recharge endpoint
fix: correct rate limit retry_after handling
docs: update OAuth2 example in README
test: add tests for authentication error handling
chore: update dependencies
```

## Release Process

Releases are automated via GitHub Actions when the version is bumped in `main`.

### For Maintainers

1. Update version in TWO places:
   - `pyproject.toml` → `version = "x.y.z"`
   - `src/polar_flow/__init__.py` → `__version__ = "x.y.z"`

2. Update `CHANGELOG.md`:
   - Move items from `[Unreleased]` to new version section
   - Add date: `## [x.y.z] - YYYY-MM-DD`

3. Commit and push to main:
   ```bash
   git add pyproject.toml src/polar_flow/__init__.py CHANGELOG.md
   git commit -m "chore: bump version to x.y.z"
   git push origin main
   ```

4. GitHub Actions will automatically:
   - Run all tests
   - Build the package
   - Publish to PyPI (using trusted publishing)
   - Create a GitHub Release with changelog excerpt

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (x.0.0) - Breaking changes
- **MINOR** (0.x.0) - New features (backwards compatible)
- **PATCH** (0.0.x) - Bug fixes

## Automated Tools

### Dependabot

- Automatically creates PRs for dependency updates
- Minor/patch updates are auto-merged if tests pass
- Major updates require manual review

### Claude Code Review

- AI-powered code review on all PRs
- Checks for type safety, test coverage, code quality
- Reviews are advisory, not blocking

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/StuMason/polar-flow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/StuMason/polar-flow/discussions)
- **Email**: stu@stumason.dev

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Respect maintainer decisions

Thank you for contributing to polar-flow! 🎉
