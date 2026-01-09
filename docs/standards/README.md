# Coding Standards

This directory contains coding standards and best practices for polar-flow development.

## Quick Navigation

- [General Standards](./general.md) - Git workflow, imports, type hints
- [Client Development](./client.md) - HTTP client patterns, error handling, rate limiting
- [Models](./models.md) - Pydantic model patterns, validation, computed properties
- [Testing](./testing.md) - Test structure, mocking, coverage requirements

## Core Principles

1. **Type Safety First** - All code must be fully typed with mypy strict mode passing
2. **Async by Default** - Primary API is async-first using httpx
3. **Test Coverage** - Minimum 80% coverage for all new code
4. **Clear Error Handling** - Use typed custom exceptions, never generic Exception
5. **Comprehensive Documentation** - All public APIs have docstrings
6. **Modern Python** - Use Python 3.11+ syntax (X | None, not Optional[X])
7. **Pydantic Models** - All API responses are validated Pydantic models
8. **Developer Experience** - Clear error messages, helpful exceptions, good defaults

## Before Committing

Always run these checks:

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy src/polar_flow

# Run tests
uv run pytest
```

All of these must pass before creating a PR.
