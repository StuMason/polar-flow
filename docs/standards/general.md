# General Coding Standards

## Git Workflow

**ALWAYS use branch-PR-review-merge workflow:**

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make changes and commit: `git commit -m "feat: add sleep endpoint"`
3. Push and create PR: `git push origin feat/your-feature`
4. Wait for CI checks and review
5. Merge to main (never force push to main)

**Never commit directly to main branch.**

## Imports

**Always import classes explicitly, never use inline FQCN:**

```python
# ✅ Good
from polar_flow.exceptions import NotFoundError

raise NotFoundError("Sleep data not found")

# ❌ Bad
import polar_flow

raise polar_flow.exceptions.NotFoundError("Sleep data not found")
```

**Group imports in order:**

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import asyncio
from datetime import date, datetime

# Third-party
import httpx
from pydantic import BaseModel, Field

# Local
from polar_flow.exceptions import NotFoundError
from polar_flow.models.sleep import SleepData
```

## Type Hints

**Type hints are MANDATORY on all functions:**

```python
# ✅ Good
async def get_sleep(self, date: str) -> SleepData:
    """Fetch sleep data."""
    ...

# ❌ Bad - missing type hints
async def get_sleep(self, date):
    ...
```

**Use modern Python 3.11+ syntax:**

```python
# ✅ Good - Modern syntax
def process(value: str | None) -> list[str]:
    ...

# ❌ Bad - Old syntax
from typing import Optional, List

def process(value: Optional[str]) -> List[str]:
    ...
```

**Use TYPE_CHECKING for forward references:**

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polar_flow.client import PolarFlow
```

## Docstrings

**All public functions/classes need docstrings (Google style):**

```python
async def get_sleep(self, user_id: str, date: str) -> SleepData:
    """Fetch sleep data for a specific date.

    Args:
        user_id: Polar user ID
        date: Date in YYYY-MM-DD format

    Returns:
        Sleep data for the specified date

    Raises:
        NotFoundError: If no sleep data exists for the date
        AuthenticationError: If access token is invalid
    """
```

## Error Handling

**Never use generic Exception:**

```python
# ✅ Good
from polar_flow.exceptions import ValidationError

if not date_is_valid(date):
    raise ValidationError(f"Invalid date format: {date}")

# ❌ Bad
if not date_is_valid(date):
    raise Exception("Invalid date")
```

## Code Style

- **Line length**: 100 characters (enforced by Ruff)
- **Indentation**: 4 spaces (never tabs)
- **Quotes**: Single quotes preferred by Ruff
- **Trailing commas**: Yes, for multiline constructs
- **Blank lines**: 2 between top-level definitions

## Naming Conventions

- **Variables/functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`
- **Modules**: `lowercase_with_underscores.py`

```python
# Good naming
class SleepData(BaseModel):
    """Sleep tracking data."""

    MAX_SLEEP_SCORE = 100

    def calculate_efficiency(self) -> float:
        """Calculate sleep efficiency."""
        return self._total_time / self._time_in_bed
```
