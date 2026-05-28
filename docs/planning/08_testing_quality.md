# 08 — Testing & Quality

> Status: Planning / Pre-Implementation
> Audience: QA / Test Architect, Backend Architect, CI/CD
> Language: English

---

## Testing Philosophy

- Test **behavior**, not implementation details
- Prioritize **integration tests** over unit tests for the booking engine — the database constraint is the source of truth for conflict prevention
- **Mock external services** (SMTP, License Broker) in all automated tests
- **Critical paths require high coverage**: license validation module and booking conflict prevention
- A failing test is never suppressed — fix the code or the test

---

## Test Types and Tools

| Type | Backend Tool | Frontend Tool | Scope |
|---|---|---|---|
| Unit | pytest | Jest | Pure functions, utilities, license validation logic |
| Integration | pytest + httpx (AsyncClient) | — | Full API flows with real PostgreSQL test DB |
| End-to-end | — | Playwright | Public booking flow, admin dashboard flows |
| Concurrency | pytest + asyncio | — | Race condition testing for booking conflict |
| Contract | pytest (mocked) | — | License validation with mocked server responses |

---

## Backend Test Structure

```
backend/
  tests/
    conftest.py                    # DB setup/teardown, license fixtures, SMTP mock
    unit/
      test_license_validation.py   # Ed25519 verification, status transitions, demo limits
      test_availability.py         # AvailabilityRule + AvailabilityException logic
      test_booking_slots.py        # Available slot calculation
    integration/
      test_booking_api.py          # Create, confirm, cancel, reschedule; conflict detection
      test_admin_api.py            # CRUD: services, staff, customers, settings
      test_license_api.py          # License status endpoint, demo mode enforcement, invalid handling
      test_auth_api.py             # Login, logout, session, lockout
      test_customer_api.py         # GDPR soft-delete, data export
    concurrency/
      test_booking_race.py         # Simultaneous booking requests → exactly one success
```

---

## Critical Test Cases (Required Before v0.1.0)

### License Validation

| Test | Expected Behavior |
|---|---|
| Valid license, active | Status = active; bookings allowed |
| No license key set | Status = missing; demo mode active |
| Demo limit reached (6th booking) | Booking creation blocked; status = missing (limit) |
| License signature tampered | Status = invalid; bookings blocked; NO demo fallback |
| License expired, grace active | Status = grace; bookings allowed; admin warning |
| License expired, grace elapsed | Status = expired; bookings blocked |
| License status = revoked (from document) | Bookings blocked; admin access remains |
| Online validation server unreachable | Status = server_unreachable; grace applied if within window |
| Admin removes invalid license | Status transitions to missing; demo mode reactivated if demo-eligible |

### Booking Conflict Prevention

| Test | Expected Behavior |
|---|---|
| Sequential non-overlapping bookings | Both succeed |
| Sequential overlapping bookings (same staff) | Second fails with HTTP 409 |
| Concurrent overlapping requests (2 threads) | Exactly one succeeds; one fails with HTTP 409 |
| Overlapping bookings for different staff | Both succeed |
| Cancelled booking slot — new booking same slot | Succeeds (cancelled bookings excluded from constraint) |

### Booking Lifecycle

| Test | Expected Behavior |
|---|---|
| Create booking → confirmation email sent | Email dispatched within test; booking status = pending |
| Admin confirms booking | Status = confirmed; customer notified |
| Admin cancels confirmed booking | Status = cancelled; customer notified |
| Booking time passes without action | Background job marks as completed or no_show [ASSUMPTION] |

### GDPR Soft-Delete

| Test | Expected Behavior |
|---|---|
| Customer GDPR delete | name/email/phone/notes nulled; gdpr_deleted_at set |
| Bookings after GDPR delete | Booking records retained (service, staff, timestamps) |
| AuditLog after GDPR delete | Deletion event recorded with actor and timestamp |

### Authentication

| Test | Expected Behavior |
|---|---|
| Correct credentials | Session cookie set; admin dashboard accessible |
| Wrong credentials | HTTP 401; no session |
| N consecutive failures | Account temporarily locked (lockout) |
| Expired session | HTTP 401; redirect to login |
| CSRF token missing on state-change | HTTP 403 |

---

## Concurrency Test: Booking Race Condition

This is a critical correctness test. The tstzrange exclusion constraint must hold under concurrent load.

```python
# tests/concurrency/test_booking_race.py

async def test_concurrent_booking_conflict():
    """Two simultaneous requests for the same staff/time must produce exactly one success."""
    import asyncio
    import httpx

    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        slot = {
            "service_id": ...,
            "team_member_id": ...,
            "start_at": "2025-06-01T10:00:00Z",
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
        }
        # Fire two requests simultaneously
        results = await asyncio.gather(
            client.post("/api/public/bookings", json=slot),
            client.post("/api/public/bookings", json=slot),
            return_exceptions=True,
        )

    statuses = [r.status_code for r in results if not isinstance(r, Exception)]
    assert statuses.count(201) == 1, "Exactly one booking must succeed"
    assert statuses.count(409) == 1, "Exactly one conflict must be returned"
```

Use `SERIALIZABLE` transaction isolation for booking creation to prevent TOCTOU races.

---

## Frontend Testing

### Component Tests (Jest + React Testing Library)

- Public booking page: renders service list, staff selector, time slot picker
- Admin calendar: renders bookings in correct time positions
- License status banner: renders correct message for each status value
- Demo mode banner: visible when status = missing (demo)

### End-to-End Tests (Playwright)

```
tests/e2e/
  booking_flow.spec.ts        # Public: select service → staff → time → submit → confirmation
  admin_booking.spec.ts       # Admin: view calendar → confirm booking → add note
  admin_license.spec.ts       # Admin: view license status; demo banner visible
  admin_auth.spec.ts          # Login → session → logout
```

Playwright tests run against a real Docker Compose stack in CI.

---

## CI Pipeline (GitHub Actions)

### Triggers
- Push to any branch
- Pull request targeting `main`

### Jobs

```yaml
jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: servario_test
          POSTGRES_USER: servario
          POSTGRES_PASSWORD: test
    steps:
      - pip install -r requirements-dev.txt
      - alembic upgrade head
      - pytest --cov=app --cov-report=xml

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - npm ci
      - npm test -- --coverage
      - npm run build

  lint:
    runs-on: ubuntu-latest
    steps:
      - ruff check .        # Python linting
      - ruff format --check .
      - eslint . --ext .ts,.tsx

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - mypy app/           # Python type checking
      - tsc --noEmit        # TypeScript type checking

  e2e:
    runs-on: ubuntu-latest
    steps:
      - docker compose up -d
      - npx playwright test
```

All jobs must pass before merge to `main`.

---

## Test Database

- Separate PostgreSQL instance for tests (not production DB)
- Created per test session via pytest fixtures
- Alembic migrations applied in test setup (`alembic upgrade head`)
- Torn down after test session
- No test state persists between test runs

```python
# conftest.py (simplified)
@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

---

## License Test Fixtures

```python
# conftest.py — license fixtures
@pytest.fixture
def valid_license_doc(test_private_key):
    """Returns a signed license document for testing."""
    payload = {
        "license_id": str(uuid4()),
        "edition": "starter",
        "max_staff": 10,
        "max_services": -1,
        "expires_at": None,
        # ... other fields
    }
    return sign_license(payload, test_private_key)

@pytest.fixture
def tampered_license_doc(valid_license_doc):
    """Returns a license document with a modified payload but unchanged signature."""
    doc = json.loads(valid_license_doc)
    doc["max_staff"] = 9999  # tamper
    return json.dumps(doc)

@pytest.fixture
def expired_license_doc(test_private_key):
    """Returns a signed license that expired in the past."""
    payload = { ..., "expires_at": "2020-01-01T00:00:00Z" }
    return sign_license(payload, test_private_key)
```

Note: test fixtures use a **test-only** Ed25519 key pair, not the production public key.

---

## Code Quality Tools

| Language | Tool | Purpose |
|---|---|---|
| Python | ruff | Linting + formatting (replaces flake8, isort, black) |
| Python | mypy | Static type checking |
| Python | bandit | Security linting (detect common vulnerabilities) |
| TypeScript | eslint | Linting with strict config |
| TypeScript | prettier | Code formatting |
| All | pre-commit | Run checks locally before commit |

### pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
  - repo: https://github.com/pre-commit/mirrors-eslint
    hooks:
      - id: eslint
        files: \.(ts|tsx)$
```

---

## Coverage Targets

| Area | Target | Rationale |
|---|---|---|
| License validation module | 90%+ | Critical correctness; security-relevant |
| Booking engine + availability logic | 85%+ | Core business logic |
| API endpoints | Integration-tested | Coverage metric less useful than behavior tests |
| Overall | No mandatory threshold for MVP | Focus on critical paths |

Coverage is measured with `pytest-cov` and reported to the CI run summary. Coverage drops below threshold on the license module fail the CI job.

---

## Performance Testing (Post-MVP)

- Load test the public booking page with **k6** or **Locust**
- Validate tstzrange constraint correctness under concurrent load (50+ simultaneous requests)
- Target: no race conditions observed in 1,000 concurrent booking attempts against the same slot
- Target: public booking page handles 100 concurrent users without degradation

---

*All items marked `[ASSUMPTION]` require project owner confirmation before implementation.*
