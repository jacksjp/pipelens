# Contributors

This project is a work in progress, and the contributor list will grow over time.

## Current Contributors

- Jayaprakash Sivanandam

## How To Be Added

If you contribute meaningful code, documentation, tests, or design work, add your name in a pull request under Current Contributors.

## Contribution Checks

- Run scripts/lint.ps1 before opening a PR.
- In check mode, scripts/lint.ps1 runs Ruff, formatting checks, mypy for Python code (apps, agents, packages), and frontend formatting/lint checks.
- The mypy step is intentional and acts as a type-safety gate for backend/shared Python changes.
