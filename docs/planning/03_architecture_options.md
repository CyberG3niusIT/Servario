# 03 — Architecture Options

_Status: Approved_
_Last updated: 2026-05-28_

---

## 1. Requirements

The architecture must satisfy the following constraints:

| Requirement | Detail |
|---|---|
| Self-hostable | Deployable by a non-expert operator via Docker Compose on a single VPS or home server |
| Single-org | One organisation per instance; no multi-tenancy at the data layer |
| Low operational complexity | Minimal moving parts; no mandatory external services beyond SMTP |
| Auditable source | BUSL-1.1 source-available; code readable and inspectable by operators |
| License validation built-in | Ed25519-signed license documents; demo/eval mode enforced in-process |
| GDPR-aware | Soft-delete for customer personal data; append-only audit log |
| Booking conflict prevention | Guaranteed at the database level, not only in application code |
| Upgrade path | Schema migrations handled by a first-class tool (Alembic); no manual SQL required |

---

## 2. Backend Options Evaluated

### Python / FastAPI (recommended)

- Async-first: `async`/`await` throughout, suitable for concurrent booking requests
- Type-safe request/response via Pydantic v2 — all API contracts are validated automatically
- Excellent developer experience: OpenAPI docs generated automatically from routes
- Strong ecosystem: SQLAlchemy 2.0, Alembic, PyNaCl/cryptography for Ed25519, APScheduler
- First-class Docker support; lightweight base images available
- Broad community adoption; easy to find contributors familiar with the stack

**Drawbacks:** Python is slower than compiled languages; not a concern at self-hosted single-org scale.

### Django

- More batteries-included (admin interface, ORM, auth)
- Django REST Framework adds a layer of abstraction that increases complexity
- ORM is less ergonomic for complex async queries than SQLAlchemy 2.0
- Built-in admin UI is not suited for a polished public-facing booking page

### Node.js / Express

- Keeps the language consistent with the Next.js frontend
- Ecosystem maturity for backend services is lower than Python for scientific/data-adjacent tooling
- Type safety requires additional tooling (TypeScript, Zod); not as seamless as Pydantic
- Mixed runtime concerns (Node version management) add operational overhead

### Go / Gin

- Compiled, fast startup, low memory footprint
- Excellent for high-throughput microservices — overkill for single-org booking platform
- Less ecosystem support for rapid feature development (ORM maturity, auth libraries)
- Smaller pool of contributors familiar with Go for an open-source project

### Recommendation: Python / FastAPI

---

## 3. Frontend Options Evaluated

### Next.js + TypeScript + Tailwind CSS + shadcn/ui (recommended)

- React-based; widest component ecosystem and hire market
- SSR and SSG: public booking page can be server-rendered for SEO and fast first paint
- App Router (Next.js 14+): supports layouts, nested routing, and React Server Components
- shadcn/ui: unstyled, accessible components that compose well with Tailwind; no lock-in
- Strong fit for the dual-surface requirement: public booking page + admin dashboard from a single codebase

### SvelteKit

- Lighter bundle, pleasant DX, growing ecosystem
- Fewer production-ready component libraries compared to React; shadcn/ui equivalent does not exist
- Smaller contributor pool for an open-source project

### Vue / Nuxt

- Viable framework, mature ecosystem
- Less community momentum for admin/SaaS dashboards compared to React in 2025–2026
- Fewer ready-made accessible UI component sets

### Recommendation: Next.js 14+ / TypeScript / Tailwind CSS / shadcn/ui

---

## 4. Database Options Evaluated

### PostgreSQL (recommended)

- `tstzrange` type with `btree_gist` exclusion constraints: the only SQL database that natively prevents overlapping booking ranges at the constraint level
- ACID-compliant; reliable for concurrent writes
- Excellent support in SQLAlchemy (including range types and JSONB)
- Mature tooling: pg_dump, pgAdmin, managed cloud versions available
- `JSONB` for flexible `changes_json` in the audit log

### SQLite

- Zero-configuration, useful for development and testing
- Write locking makes it unsuitable for production concurrent booking requests
- No support for `tstzrange` exclusion constraints
- **Decision: SQLite will be used in the test suite only; no production SQLite fallback.**

### MySQL / MariaDB

- Widely deployed; familiar to many operators
- No native range type; booking conflict prevention would require application-level logic (unreliable)
- `JSON` column support weaker than PostgreSQL `JSONB`
- Not supported by this project

### Recommendation: PostgreSQL 15+ only. No SQLite or MySQL fallback for production.

---

## 5. Reverse Proxy Options Evaluated

### Nginx Proxy Manager (recommended standard)

- Web GUI for creating proxy hosts and managing certificates — accessible to non-expert operators
- Automatic HTTPS via Let's Encrypt (HTTP-01 and DNS-01 challenge support)
- Docker-native; ships as a container alongside Servario in the same Compose file
- Widely adopted in the self-hosting community; extensive tutorials available

### Caddy

- Automatic HTTPS by default; minimal configuration
- JSON or Caddyfile config — simpler than Nginx directives
- Good alternative for operators who prefer a config-file approach without a GUI
- Documented as an alternative in the deployment guide

### Plain Nginx

- Maximum configurability; no GUI dependency
- Steeper configuration curve; HTTPS setup is manual
- Appropriate for advanced operators or production environments with existing Nginx infrastructure
- Documented as an alternative in the deployment guide

### Recommendation: Nginx Proxy Manager as the default in `docker-compose.yml`. Caddy and plain Nginx documented as alternatives.

---

## 6. Background Jobs

### Celery + Redis

- Industry-standard task queue; supports retries, scheduling, and priority queues
- Requires an additional Redis container — increases operational complexity
- Appropriate when job volume, reliability, or observability requirements are high
- Recommended migration path post-MVP if job volume or failure-rate requirements demand it

### APScheduler (in-process)

- Runs inside the FastAPI process; zero additional containers
- Suitable for the MVP workload: reminder emails, periodic license re-validation
- No persistent job queue — jobs lost on process restart (acceptable for notifications at MVP scale)
- [ASSUMPTION] Average instances will process fewer than 100 bookings/day; in-process scheduling is sufficient for MVP

### Recommendation: APScheduler for MVP. Celery + Redis documented as an upgrade path post-MVP.

---

## 7. Final Recommended Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+ / FastAPI |
| ORM / Migrations | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 15+ |
| Booking conflict prevention | `tstzrange` exclusion constraint (`btree_gist` extension) |
| Background jobs | APScheduler (MVP); Celery + Redis (post-MVP option) |
| Frontend | Next.js 14+ / TypeScript / Tailwind CSS / shadcn/ui |
| Reverse proxy | Nginx Proxy Manager (standard deployment) |
| Deployment | Docker Compose |
| License | BUSL-1.1 |
| License validation | Ed25519-signed license documents (PyNaCl or `cryptography` library) |
| Billing | RevenueCat → License Broker (private) |

---

## 8. System Components Diagram

```
┌─────────────────────────────────────────────┐
│         Public Booking Page (Next.js)        │
└────────────────────┬────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────┐
│           Nginx Proxy Manager                │
│   (TLS termination, reverse proxy, GUI)      │
└────────────────────┬────────────────────────┘
                     │ HTTP (internal)
┌────────────────────▼────────────────────────┐
│             FastAPI Backend                  │
│                                             │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ PostgreSQL  │  │   License Module     │  │
│  │             │  │ (Ed25519 validation, │  │
│  │ bookings    │  │  demo mode enforce-  │  │
│  │ services    │  │  ment, status cache) │  │
│  │ staff       │  └──────────────────────┘  │
│  │ settings    │  ┌──────────────────────┐  │
│  │ audit log   │  │    APScheduler       │  │
│  └─────────────┘  │ (email notifications,│  │
│                   │  license re-check)   │  │
│                   └──────────────────────┘  │
└─────────────────────────────────────────────┘

         Billing / License flow (external):

  ┌─────────────┐     ┌──────────────────────┐
  │ RevenueCat  │────▶│  License Broker      │
  │ (billing)   │     │  (private system,    │
  └─────────────┘     │   not in public repo)│
                      └──────────┬───────────┘
                                 │ issues
                      ┌──────────▼───────────┐
                      │  Signed License Doc  │
                      │  (Ed25519 signature) │
                      └──────────┬───────────┘
                                 │ operator configures
                      ┌──────────▼───────────┐
                      │ SERVARIO_LICENSE_KEY  │
                      │   env var / file      │
                      └──────────────────────┘
```

---

## 9. Architectural Decision Records (ADRs)

### ADR-001 — Single-org model (no `org_id` in domain tables)

**Status:** Accepted

**Context:** Servario is a self-hosted platform. Each deployment serves exactly one business.

**Decision:** No `org_id` column in domain tables (`bookings`, `services`, `team_members`, etc.). A single `settings` table row holds instance configuration.

**Rationale:** Adding `org_id` everywhere for a single-org use case adds schema complexity, query noise, and opportunities for data leakage bugs (missing `WHERE org_id = ?`). If multi-tenancy is ever required, it will be a separate edition with an explicit migration.

**Consequences:** The schema is simpler. Multi-tenancy cannot be bolted on without a migration. This is intentional.

---

### ADR-002 — `tstzrange` exclusion constraint for booking conflict prevention

**Status:** Accepted

**Context:** Booking conflicts (two overlapping appointments for the same staff member) must be prevented reliably, including under concurrent HTTP requests.

**Decision:** Use a PostgreSQL `EXCLUDE USING gist` constraint with `btree_gist` and `tstzrange`, rather than a partial unique index or application-level locking.

**Rationale:** A partial unique index can only prevent exact-start duplicates. Application-level checks are subject to race conditions. The exclusion constraint is enforced atomically by the database engine regardless of concurrency.

**Consequences:** PostgreSQL is the only supported database. SQLite and MySQL cannot enforce this constraint and are not supported for production.

---

### ADR-003 — Ed25519 for license document signing

**Status:** Accepted

**Context:** License documents must be verifiable by self-hosted instances without contacting an external server at runtime.

**Decision:** License documents are signed with Ed25519 (via the License Broker). The Servario application verifies signatures using the embedded public key.

**Rationale:** Ed25519 offers a fast, secure, and simple API. No certificate infrastructure is required. The private signing key stays in the License Broker (never in the public codebase). PyNaCl and the `cryptography` library both provide reliable Ed25519 support in Python.

**Consequences:** License forgery requires the private key, which is never distributed. Offline validation is possible. The public key is embedded in the application binary/source.

---

### ADR-004 — RevenueCat as the billing layer

**Status:** Accepted

**Context:** Subscription management (trials, upgrades, downgrades, failed payments, invoices) is complex to build and maintain.

**Decision:** RevenueCat handles subscription lifecycle and webhooks. The License Broker translates RevenueCat events into signed license documents.

**Rationale:** RevenueCat reduces billing complexity significantly. It supports web purchases and multiple payment processors. The License Broker is the only system that holds RevenueCat secret keys.

**Consequences:** Servario's billing path requires an active License Broker deployment. Self-hosted instances do not need internet access for day-to-day operation (offline grace period supported).

---

### ADR-005 — License Broker is a private system not in the public repository

**Status:** Accepted

**Context:** RevenueCat secret keys must never appear in the source-available Servario codebase.

**Decision:** The License Broker is a separate, privately hosted service. Its source code is not included in the public Servario repository.

**Rationale:** BUSL-1.1 makes the Servario source code publicly readable. Any secret key embedded in that source would be compromised. By keeping the Broker private, the signing key and RevenueCat credentials are fully isolated from the open codebase.

**Consequences:** The billing-to-license flow is not auditable by the community. This is an accepted trade-off for security. The Ed25519 public key (used for verification) is public; only the private key is secret.
