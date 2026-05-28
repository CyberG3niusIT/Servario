# Servario — Master Plan

> **Servario** is a self-hosted, source-available appointment and service booking
> platform for small and medium-sized businesses.

**License:** Source Available under BUSL-1.1 — production use requires a license.  
**Status:** Pre-implementation / Planning

---

## Table of Contents

| # | Document | Purpose |
|---|----------|---------|
| — | [PLAN.md](./PLAN.md) *(this file)* | Central overview, architecture snapshot, open decisions |
| 00 | [docs/planning/00_repository_status.md](./docs/planning/00_repository_status.md) | Repository state, gaps, pre-implementation checklist |
| 10 | [docs/planning/10_next_steps.md](./docs/planning/10_next_steps.md) | Implementation phases, risk register, definition of "ready" |
| 11 | [docs/planning/11_license_model.md](./docs/planning/11_license_model.md) | Full license architecture, billing system, demo/eval mode |

---

## Planning Documents — Quick Summary

| Document | Purpose | Status |
|----------|---------|--------|
| `00_repository_status.md` | Snapshot of repo state; pre-implementation checklist | Planning / Not Started |
| `10_next_steps.md` | Implementation phases, risk register | Planning / Not Started |
| `11_license_model.md` | BUSL-1.1 rationale, Ed25519 licenses, RevenueCat, demo mode | Planning / Not Started |

---

## Architecture Snapshot

```
┌─────────────────────────────────────────────────────────┐
│                     Reverse Proxy                        │
│          Nginx Proxy Manager (standard)                  │
│          Caddy / plain Nginx (alternatives)              │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
          ┌─────────────┴─────────────┐
          │                           │
   ┌──────▼──────┐             ┌──────▼──────┐
   │  Next.js    │             │   FastAPI   │
   │  Frontend   │◄──REST/WS──►│   Backend   │
   │  (Node.js)  │             │  (Python)   │
   └─────────────┘             └──────┬──────┘
                                      │
                               ┌──────▼──────┐
                               │ PostgreSQL  │
                               │  (primary   │
                               │  datastore) │
                               └─────────────┘
```

### Component Summary

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend API | Python / FastAPI | Async; Ed25519 license validation built in |
| Frontend | Next.js (React) | Server-side rendering; admin UI + public booking page |
| Database | PostgreSQL | `tstzrange` exclusion constraint for booking conflict prevention |
| Deployment | Docker Compose | Single `docker-compose.yml` for the full stack |
| Reverse Proxy | Nginx Proxy Manager | Standard; Caddy and plain Nginx supported as alternatives |
| Migrations | Alembic [ASSUMPTION] | Standard FastAPI / SQLAlchemy migration tooling |

---

## License System Snapshot

```
  Customer pays
       │
       ▼
  RevenueCat ──► entitlement granted
       │
       ▼
  License Broker (private infrastructure)
       │  generates
       ▼
  Ed25519-signed license document
  { edition, expiry, domain, limits, signature }
       │
       ▼
  Servario instance validates on startup + periodically
       │
       ├── Valid + edition limits OK  →  normal operation
       ├── Demo mode (no license)     →  max 5 bookings / 2 staff / 3 services / 30 days
       └── Invalid / expired          →  read-only / locked
```

### Editions

| Edition | Intended Audience |
|---------|------------------|
| `starter` | Freelancers, sole traders |
| `professional` | Small teams |
| `business` | Multi-staff SMBs |

> There is no "community" edition. Demo/eval mode is the only free tier and is
> time- and resource-limited (see above).

See [docs/planning/11_license_model.md](./docs/planning/11_license_model.md) for
the full license architecture.

---

## Open Decisions

The following decisions must be confirmed before the relevant implementation
phase begins. Items marked **Resolved** are closed; all others require an
explicit confirmation from the project owner.

| ID | Question | Recommendation | Status |
|----|----------|---------------|--------|
| E1 | Stack: FastAPI + Next.js + PostgreSQL? | Confirmed | Open |
| E2 | Only PostgreSQL or SQLite fallback? | Only PostgreSQL for MVP | Open |
| E3 | Next.js or SvelteKit for the frontend? | Next.js | Open |
| E4 | Session-based auth only, or OAuth as well? | Session only for MVP | Open |
| E5 | SMTP only for notifications, or webhooks/SMS too? | SMTP only for MVP | Open |
| E6 | No `org_id` in MVP schema (single-org model) | Option A confirmed | Resolved |
| E7 | BUSL-1.1 as final license? | BUSL-1.1 recommended | To confirm |
| E8 | Demo mode limits (5 bookings / 2 staff / 3 services / 30 days)? | Proposal in `11_license_model.md` | To confirm |
| E9 | CLA requirement for external contributions? | Required | Text to define |
| E10 | License Broker: own infrastructure or third-party service? | Private system | To decide |
| E11 | RevenueCat as billing system? | Yes, preferred | To confirm |
| E12 | RevenueCat entitlement ID mapping? | `servario_starter` / `servario_professional` / `servario_business` | To confirm |

Decisions **E7, E8, E9, E10, E11, E12** must be confirmed before any code
touching the license, billing, or authentication subsystems is merged.

---

## Agent Roles

The following agent roles are defined for the project. Each agent owns a
specific domain and is accountable for decisions within it.

| # | Role |
|---|------|
| 1 | Product Architect |
| 2 | Repository & Community Maintainer |
| 3 | Backend Architect |
| 4 | Frontend / UX Architect |
| 5 | Security & Privacy Reviewer |
| 6 | DevOps / Self-Hosting Architect |
| 7 | QA / Test Architect |
| 8 | Documentation & README Designer |
| 9 | Licensing & Commercial Model Reviewer |
| 10 | RevenueCat Licensing Architect |

---

## Next Steps

See [docs/planning/10_next_steps.md](./docs/planning/10_next_steps.md) for the
full phase-by-phase implementation plan and risk register.

**Immediate priority:** complete the Phase 0 pre-implementation checklist in
[docs/planning/00_repository_status.md](./docs/planning/00_repository_status.md)
before writing any application code.
