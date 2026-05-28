# 10 — Next Steps & Implementation Plan

> **Purpose:** Phase-by-phase implementation order, open decisions that must be
> resolved before coding begins, risk register, and the definition of
> "implementation ready."

---

## 1. Implementation Phases

### Phase 0 — Pre-Implementation (Repository Hygiene)

> **Gate:** Nothing in Phase 1 or later may be merged until all Phase 0 items
> are complete. See the full checklist in
> [00_repository_status.md](./00_repository_status.md).

| Task | Owner Role | Notes |
|------|-----------|-------|
| Replace AGPL-3.0 and "open-source" badges in `README.md` | Repository & Community Maintainer | Highest priority; legal risk |
| Create `LICENSE` file (BUSL-1.1, all fields filled) | Licensing & Commercial Model Reviewer | Blocks all other work |
| Create `.gitignore` (Python, Node.js, Docker, OS, IDE) | Repository & Community Maintainer | Must exist before any source file is committed |
| Create `CONTRIBUTING.md` with CLA note | Repository & Community Maintainer | Decision E9 must be resolved first |
| Create `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1) | Repository & Community Maintainer | — |
| Create `SECURITY.md` | Security & Privacy Reviewer | Include responsible-disclosure e-mail and response SLA |
| Create GitHub issue and PR templates | Repository & Community Maintainer | `.github/ISSUE_TEMPLATE/` + `pull_request_template.md` |
| Create `docker-compose.yml` skeleton | DevOps / Self-Hosting Architect | Services: `api`, `frontend`, `db`, `proxy` |
| Create `.env.example` skeleton | DevOps / Self-Hosting Architect | All keys present; no real secrets |

---

### Phase 1 — FastAPI Skeleton + License Module + DB Models + Auth

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Initialise FastAPI project structure | Backend Architect | Phase 0 complete |
| Implement Ed25519 license validation module | RevenueCat Licensing Architect | E7, E10 confirmed |
| Implement demo mode enforcement | Backend Architect | E8 confirmed; license module done |
| Define PostgreSQL schema and Alembic migrations [ASSUMPTION] | Backend Architect | E1, E2 confirmed |
| Implement session-based authentication | Backend Architect | E4 confirmed |
| Set up basic CI pipeline (lint, test, type-check) | QA / Test Architect | Phase 0 complete |

**Exit criteria:** FastAPI starts, license module validates a test key,
demo mode limits are enforced, a single admin user can authenticate, and
Alembic migrations run cleanly against a local PostgreSQL instance.

---

### Phase 2 — Scheduling Engine + Conflict Prevention + Concurrency Tests

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Implement `tstzrange` exclusion constraint (with `btree_gist`) | Backend Architect | Phase 1 complete |
| Implement booking slot availability logic | Backend Architect | DB schema stable |
| Implement serializable transaction wrapper for booking creation | Backend Architect | Constraint in place |
| Write concurrency tests (simultaneous booking for same slot) | QA / Test Architect | Scheduling engine done |

**Exit criteria:** Concurrent booking requests for the same time slot result in
exactly one success and one conflict error, verified by automated tests.

---

### Phase 3 — Admin UI + License Status Display

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Initialise Next.js project structure | Frontend / UX Architect | Phase 1 complete |
| Implement admin dashboard shell | Frontend / UX Architect | — |
| Implement license status page (edition, expiry, limits) | Frontend / UX Architect | License module done |
| Implement staff management UI | Frontend / UX Architect | DB models done |
| Implement service catalogue management UI | Frontend / UX Architect | DB models done |

**Exit criteria:** Admin can log in, view license status, and manage staff and services.

---

### Phase 4 — Public Booking Page

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Implement public-facing service selection page | Frontend / UX Architect | Phase 3 complete |
| Implement time slot picker (availability-aware) | Frontend / UX Architect | Scheduling engine done |
| Implement booking confirmation flow | Frontend / UX Architect | — |
| Accessibility and mobile responsiveness review | Frontend / UX Architect | Booking flow done |

**Exit criteria:** A customer can browse available services, select a slot,
and confirm a booking without an account.

---

### Phase 5 — Email Notifications

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Implement SMTP notification module | Backend Architect | E5 confirmed; Phase 4 complete |
| Booking confirmation e-mail to customer | Backend Architect | SMTP module done |
| Booking notification e-mail to staff member | Backend Architect | SMTP module done |
| Cancellation and reminder e-mails | Backend Architect | — |

**Exit criteria:** A confirmed booking triggers e-mails to both the customer
and the assigned staff member, verified by integration tests against a local
mail catcher [ASSUMPTION: Mailpit or MailHog].

---

### Phase 6 — Finalization, Docker Packaging, Documentation, v0.1.0

| Task | Owner Role | Dependencies |
|------|-----------|--------------|
| Finalize `docker-compose.yml` for production use | DevOps / Self-Hosting Architect | All phases complete |
| Write self-hosting installation guide | Documentation & README Designer | Docker packaging done |
| Write user documentation (admin and booking) | Documentation & README Designer | — |
| Security review of the full codebase | Security & Privacy Reviewer | All phases complete |
| Final QA pass and test coverage review | QA / Test Architect | All phases complete |
| Tag `v0.1.0` and publish release notes | Repository & Community Maintainer | All gates passed |

**Exit criteria:** The full stack starts from `docker-compose up`, the
installation guide is complete, test coverage meets the agreed threshold
[ASSUMPTION: 70% line coverage minimum], and the security review has no
outstanding high-severity findings.

---

## 2. Open Decisions to Confirm Before Implementation

The following decisions from `PLAN.md` must be resolved before the indicated
phase begins. Writing code that depends on an unresolved decision is not
permitted.

| Decision ID | Question | Blocks | Reference |
|-------------|----------|--------|-----------|
| E1 | Stack: FastAPI + Next.js + PostgreSQL? | Phase 1 | [PLAN.md](../../PLAN.md) |
| E2 | Only PostgreSQL, or SQLite fallback? | Phase 1 | [PLAN.md](../../PLAN.md) |
| E3 | Next.js or SvelteKit? | Phase 3 | [PLAN.md](../../PLAN.md) |
| E4 | Session auth only, or OAuth? | Phase 1 | [PLAN.md](../../PLAN.md) |
| E5 | SMTP only, or webhooks/SMS? | Phase 5 | [PLAN.md](../../PLAN.md) |
| E7 | BUSL-1.1 as final license? | Phase 0 (LICENSE file) | [PLAN.md](../../PLAN.md) |
| E8 | Demo mode limits confirmed? | Phase 1 (demo mode) | [PLAN.md](../../PLAN.md) |
| E9 | CLA text defined? | Phase 0 (CONTRIBUTING.md) | [PLAN.md](../../PLAN.md) |
| E10 | License Broker: own infra or service? | Phase 1 (license module) | [PLAN.md](../../PLAN.md) |
| E11 | RevenueCat as billing system? | Phase 1 (license module) | [PLAN.md](../../PLAN.md) |
| E12 | RevenueCat entitlement ID mapping? | Phase 1 (license module) | [PLAN.md](../../PLAN.md) |

---

## 3. Risk Register

| Risk | Likelihood | Severity | Mitigation |
|------|-----------|----------|-----------|
| License check code is removed from a fork | Medium | High | Fair pricing that makes compliance easier than circumvention; periodic license validation on startup and at runtime; no DRM escalation — keep the system honest and light |
| BUSL-1.1 rejected by enterprise procurement departments | Low–Medium | Medium | Primary target audience is SMBs, not enterprises; BUSL-1.1 is well-known (used by HashiCorp, Sentry, MariaDB); the Change Date converts to Apache 2.0 |
| CLA requirement deters contributors | Medium | Medium | Keep the CLA short, plain-language, and fair; avoid corporate assignment clauses; clearly explain why it is needed for a commercial project |
| GDPR risk in license validation | Low–Medium | High | Collect minimal data; the `domain` field in the license document is optional; publish a privacy notice covering license validation data; do not log IP addresses in the broker |
| Booking race condition (double-booking) | Low | High | `tstzrange` exclusion constraint with `btree_gist` at the database level; serializable transaction isolation for booking creation; automated concurrency tests in CI (Phase 2) |
| Single-maintainer burnout before v0.1.0 | Medium | High | Document all processes and decisions in this planning folder; identify and onboard a co-maintainer before the public release; keep the MVP scope minimal |
| Incorrect license badge causes community backlash | High (if uncorrected) | High | Phase 0 item #1 — must be corrected immediately; this is the highest-priority single action in the project |

---

## 4. Definition of "Implementation Ready"

The project is considered **implementation ready** (i.e., Phase 1 may begin)
when all of the following conditions are met:

1. **All Phase 0 checklist items are complete** — see
   [00_repository_status.md](./00_repository_status.md) for the full list.
2. **All open decisions that block Phase 1 are resolved** — specifically E1,
   E2, E4, E7, E8, E9, E10, E11, E12 from the table above.
3. **The `main` branch contains:**
   - A valid `LICENSE` file (BUSL-1.1, all fields filled).
   - Corrected `README.md` (no AGPL-3.0 badge, no "open-source" badge).
   - `.gitignore` covering all relevant artefacts.
   - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.
   - `docker-compose.yml` and `.env.example` skeletons.
4. **CI passes** on the main branch (at minimum: lint and basic health check).
5. **No unresolved high-severity findings** from the initial security review
   of the repository structure and configuration.
