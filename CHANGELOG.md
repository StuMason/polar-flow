# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffolding with uv and hatchling
- Custom exception hierarchy (PolarFlowError, AuthenticationError, RateLimitError, NotFoundError, ValidationError)
- Comprehensive test suite with pytest, pytest-asyncio, pytest-httpx
- Ruff for linting and formatting
- mypy strict mode type checking
- GitHub Actions workflows (tests, lint, publish, claude-code-review, dependabot-automerge)
- Pre-commit hooks for code quality
- Documentation: README, CLAUDE.md, CONTRIBUTING.md
- 80%+ test coverage requirement
- Core async HTTP client (`PolarFlow`) with httpx
- OAuth2 authentication handler (`OAuth2Handler`) for authorization code flow
- Sleep endpoint with full type safety (`SleepEndpoint`)
  - Get sleep data for specific date
  - List sleep data for multiple days
- Pydantic models for sleep data with computed properties
  - Sleep score, duration, efficiency
  - Sleep stages (light, deep, REM)
  - Heart rate and HRV metrics
  - Computed properties: total_sleep_hours, sleep_efficiency, time_in_bed_hours
- Comprehensive error handling with typed exceptions
- Rate limit awareness with header checking
- Full test coverage (92%) for all components
- Example script demonstrating OAuth flow and sleep data retrieval

## [0.1.0] - TBD

Initial release.
