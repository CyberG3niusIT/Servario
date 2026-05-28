# Contributing to Servario

Thank you for your interest in contributing to Servario.

## License and Contributor Agreement

Servario is source-available software licensed under the Business Source License 1.1 (BUSL-1.1).
Production use requires a valid commercial license.

By submitting a pull request or patch, you agree that your contribution:

- Is your original work or you have the right to submit it
- Is submitted under the same terms as the project license
- Grants the project maintainer the right to distribute your contribution
  under the project's current and future license terms (including commercial distribution)

A formal Contributor License Agreement (CLA) process will be introduced before
the first public release. Until then, the above understanding applies to all contributions.

## How to Contribute

1. Check the [open issues](../../issues) for bugs or feature requests
2. For significant changes, open an issue first to discuss the approach
3. Fork the repository and create a branch from `main`
4. Write code following the conventions described below
5. Add or update tests for your change
6. Submit a pull request against `main`

## Code Conventions

**Python (backend)**
- Formatter: `ruff format`
- Linter: `ruff check`
- Type checking: `mypy`
- Style: follow existing patterns; no commented-out code

**TypeScript (frontend)**
- Formatter: `prettier`
- Linter: `eslint`
- Type checking: `tsc --noEmit`

## Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## What We Do Not Accept

- Changes that remove or bypass the license validation module
- Changes that introduce telemetry without explicit operator opt-in
- Dependencies with licenses incompatible with BUSL-1.1

## Questions

Open an issue or start a discussion in the repository.
