# 05 — MVP Scope

> Status: Planning / Pre-Implementation
> Audience: Product Architect, QA Architect, all agents
> Language: English

---

## Definition of MVP

The minimum feature set that allows a real service business to go live, accept bookings from real customers, and manage those bookings through an admin interface — with a production-grade license system from day one.

---

## In Scope — MVP

### Core Booking Features

| Feature | Description |
|---|---|
| Service catalog | Create, update, and deactivate services (name, duration, price, description) |
| Staff management | Create team members, assign services, set availability rules and exceptions |
| Public booking page | Unauthenticated; customers select service → staff → date/time → submit |
| Booking confirmation | Customer receives confirmation email; booking appears in admin |
| Admin calendar view | View all bookings in calendar layout (day/week view) |
| Booking list | Filterable/sortable list of all bookings |
| Booking actions | Confirm, cancel, reschedule, add internal notes |
| Customer records | Created automatically on booking; GDPR-compliant soft-delete |
| Email notifications | Confirmation, reminder (24h before appointment), cancellation |
| Settings | Business info, timezone, SMTP configuration |
| Admin authentication | Email/password login, session-based, bcrypt password hashing |
| Conflict prevention | tstzrange exclusion constraint prevents double-booking |

### License System (required before any production deployment)

| Requirement | Details |
|---|---|
| License file parsing | Read from `SERVARIO_LICENSE_KEY` env var or `/data/license.json` |
| Ed25519 signature verification | At backend startup; against compiled-in public key |
| License status in Admin UI | Badge showing current status with actionable message |
| Demo/Eval mode | Hard limits enforced (see Demo Mode section below) |
| `invalid` → no demo fallback | A tampered/invalid license does not trigger demo mode |
| `missing` → demo until limits | License missing → demo mode until limits reached |
| Booking block on expired/invalid/revoked | New booking creation blocked; data and admin access remain |
| Environment variables | `SERVARIO_LICENSE_KEY`, `SERVARIO_INSTANCE_ID`, `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` |

### Deployment

| Requirement | Details |
|---|---|
| Docker Compose | Single `docker compose up -d` starts all services |
| Nginx Proxy Manager | Default reverse proxy in docker-compose.yml |
| .env.example | All required variables documented with comments |
| Alembic migrations | Auto-applied on backend startup |
| Health endpoint | `GET /api/health` returns version, DB status, license status |

---

## Demo/Eval Mode — Hard Limits

When `SERVARIO_LICENSE_KEY` is not set and the instance has not yet exceeded demo limits, Servario operates in Demo/Eval mode:

| Limit | Value |
|---|---|
| Maximum total bookings stored | 5 |
| Maximum staff members | 2 |
| Maximum services | 3 |
| Maximum calendar days from first startup | 30 |

When any limit is reached:
- New bookings, staff creation, and service creation are blocked via API
- Existing data remains fully readable and exportable
- Admin dashboard shows a prominent license acquisition prompt
- Public booking page shows a "service temporarily unavailable" message [ASSUMPTION: exact message TBD]

Demo mode is explicitly displayed in the admin UI with a persistent banner. It is **not** a paid tier and does not correspond to any RevenueCat entitlement or license edition field.

---

## Out of Scope — MVP (Explicitly Deferred)

### Payment Processing
- Online payment at booking time (Stripe, PayPal, etc.)
- Invoice generation
- Refund management

### Customer Accounts
- Customer login / account portal
- Customer booking history view
- Customer self-cancellation portal (admin-managed cancellation is in scope)

### Advanced Authentication
- OAuth / SSO for admin login
- Two-factor authentication (2FA) / MFA
- API keys for external integrations

### Advanced Scheduling
- Multi-timezone per staff member (single business timezone in scope)
- Recurring bookings / subscription appointments
- Group bookings (multiple customers per slot)
- Waiting list
- Buffer time between bookings [ASSUMPTION: may be added as a simple field post-MVP]

### Advanced Features
- Online payment integration
- Plugin / webhook API for external integrations
- White-labeling / custom domains per staff member
- Mobile app (iOS/Android)
- Embeddable booking widget

### License System (Post-MVP)
- Online validation against License Broker
- Admin UI: license entry form (no restart required)
- Edition-based feature flags (Starter/Professional/Business differentiation)
- Automatic renewal reminders

### Infrastructure
- Kubernetes / Helm chart deployment
- Multi-region deployment
- High-availability / read replicas

---

## License Module — MVP Requirements Detail

### Status Handling

| Status | New bookings | Admin access | Data export | Behavior |
|---|---|---|---|---|
| `active` | Allowed | Yes | Yes | Normal operation |
| `grace` | Allowed | Yes | Yes | Warning banner in admin UI |
| `server_unreachable` | Depends on grace_until | Yes | Yes | Warning banner |
| `missing` (demo OK) | Allowed (demo) | Yes | Yes | Demo banner |
| `missing` (demo limit) | Blocked | Yes | Yes | License acquisition prompt |
| `expired` (grace active) | Allowed | Yes | Yes | Warning banner |
| `expired` (grace elapsed) | Blocked | Yes | Yes | License acquisition prompt |
| `invalid` | Blocked | Yes | Yes | No demo fallback; diagnostic message |
| `revoked` | Blocked | Yes | Yes | License acquisition prompt |

### Required Environment Variables

```env
SERVARIO_LICENSE_KEY=                  # base64-encoded signed license JSON or file path
SERVARIO_INSTANCE_ID=                  # auto-generated UUID on first start; persisted to /data/instance_id
SERVARIO_LICENSE_OFFLINE_GRACE_DAYS=30 # default 30; range 1–90
```

No RevenueCat keys in the self-hosted instance. License validation uses only the Ed25519 public key compiled into the backend.

---

## Acceptance Criteria

### Public Booking Flow
1. Customer visits the public booking page URL
2. Selects a service from the available services
3. Selects a staff member (or "any available")
4. Selects a date and time from available slots
5. Enters name and email
6. Submits the booking
7. Receives a confirmation email within 60 seconds
8. Booking appears in the admin calendar immediately

### Booking Conflict Prevention
1. Two simultaneous POST requests for the same staff member and overlapping time slot
2. Exactly one request succeeds (HTTP 201)
3. The other request fails (HTTP 409 Conflict)
4. No double-booking in the database

### License — Demo Mode Enforcement
1. Instance starts with no `SERVARIO_LICENSE_KEY`
2. Demo banner visible in admin UI
3. Bookings 1–5 succeed
4. Booking 6 is blocked (HTTP 402 or 403 with clear message)
5. Admin dashboard shows license acquisition prompt

### License — Invalid Handling
1. Instance starts with a tampered or incorrectly signed license
2. Status is `invalid`
3. New booking creation returns an error (no demo fallback)
4. Admin can access dashboard, view data, and export
5. Admin removes invalid license key → instance transitions to `missing` status

### Email Notifications
1. Booking confirmed → customer receives confirmation email with booking details
2. 24 hours before appointment → customer receives reminder email
3. Booking cancelled → customer receives cancellation email

### Admin Authentication
1. Login with correct credentials → session cookie set, admin dashboard accessible
2. Login with incorrect credentials → error message, no session
3. After N failed attempts → account temporarily locked [ASSUMPTION: N = 5, lockout = 15 minutes]

---

## Definition of Done (v0.1.0)

The following conditions must all be met before v0.1.0 can be released:

- [ ] All MVP acceptance criteria pass
- [ ] Unit tests cover license validation module at 90%+ coverage
- [ ] Integration test: full booking flow (public page → admin confirmation → notification email)
- [ ] Concurrency test: simultaneous booking requests produce exactly one success
- [ ] Docker Compose starts successfully with a fresh database
- [ ] README Quick Start works: clone → copy `.env.example` → `docker compose up -d` → book an appointment
- [ ] `LICENSE` file contains BUSL-1.1 text with all required fields filled in
- [ ] No AGPL-3.0 references anywhere in the repository
- [ ] No `community` edition references in any code, configuration, or documentation
- [ ] `.env.example` contains no RevenueCat keys
- [ ] GDPR soft-delete works: customer data nulled, booking history retained
- [ ] Audit log records all required events (booking lifecycle, admin actions, license changes)
- [ ] Health endpoint (`GET /api/health`) returns correct status
- [ ] `CONTRIBUTING.md` with CLA note present
- [ ] `SECURITY.md` present

---

*All items marked `[ASSUMPTION]` require project owner confirmation before implementation.*
