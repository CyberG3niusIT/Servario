# 00 — Repository Status & Pre-Implementation Checklist

> **Purpose:** Snapshot of the current repository state, identified gaps, and a
> gating checklist that must be completed before any application code is written.

---

## 1. Current State of the Repository

| Item | Present? | Notes |
|------|----------|-------|
| `README.md` | Yes | Contains project description and an **incorrect** AGPL-3.0 license badge |
| `LICENSE` | No | Legal gap — must be created before any public visibility |
| `.gitignore` | No | Must be created before the first code commit |
| `Dockerfile` / `docker-compose.yml` | No | Needed for self-hosting packaging |
| `.env.example` | No | Required alongside Docker Compose |
| Application source code | No | Backend and frontend do not yet exist |
| `CONTRIBUTING.md` | No | Needed before accepting any outside contributions |
| `CODE_OF_CONDUCT.md` | No | Standard community health file |
| `SECURITY.md` | No | Required for responsible disclosure |
| GitHub issue / PR templates | No | Improves contributor and reporter experience |
| `docs/` directory | Partially | Only the planning folder exists |

**Active branch:** `claude/elegant-hypatia-8qzQY`

---

## 2. What the README.md Currently Contains

- A headline description identifying Servario as a scheduling and appointment platform.
- A license badge referencing **AGPL-3.0** — this is **incorrect** and must be replaced immediately.
- An "open-source" badge — also incorrect; Servario is **source-available**, not open source.
- A feature list describing booking, staff, and service management modules.
- A mention of the intended technology stack (Python/FastAPI, Next.js, PostgreSQL).
- A project status table indicating "early planning."

---

## 3. Gaps and Issues

### 3.1 Incorrect License Badge

The `README.md` displays an AGPL-3.0 badge. Servario is licensed under
**BUSL-1.1 (Business Source License 1.1)**, which is a **source-available**
license, not an open-source license. The AGPL-3.0 badge creates false
expectations for developers, contributors, and potential enterprise customers and
must be corrected before the repository has any public visibility.

Additionally, there is an "open-source" badge that must also be removed or
replaced. BUSL-1.1 is explicitly not an OSI-approved open-source license.

**Required replacement:** A `Source Available — BUSL-1.1` badge and a
plain-text notice clarifying that production use requires a paid license.

### 3.2 No LICENSE File

Without a `LICENSE` file the repository has no enforceable terms. Anyone
cloning the repository operates in a legal grey area. BUSL-1.1 must be placed
in the repository root with all template fields filled in:

| BUSL-1.1 Field | Value |
|---|---|
| Licensor | [ASSUMPTION: Legal entity name to be confirmed by project owner] |
| Licensed Work | Servario |
| Additional Use Grant | Internal non-production use only; production commercial use requires a paid license |
| Change Date | [ASSUMPTION: 4 years from first public release, e.g. 2029-01-01] |
| Change License | Apache License 2.0 |

### 3.3 No `.gitignore`

Committing without a `.gitignore` risks accidentally committing `.env` files,
Python virtual environments (`venv/`, `.venv/`), `node_modules/`, IDE
configuration (`.idea/`, `.vscode/`), and compiled build artifacts. This file
must exist before any source code is added to the repository.

### 3.4 No Docker Files

Servario is a self-hosted product. Docker Compose packaging is the primary
distribution and deployment mechanism. Skeleton files (`docker-compose.yml`,
`.env.example`) should be established early to validate the deployment model
before the application is feature-complete.

The standard deployment topology is:

```
services:
  api          # FastAPI backend
  frontend     # Next.js frontend
  db           # PostgreSQL
  proxy        # Nginx Proxy Manager (standard); Caddy / plain Nginx as alternatives
```

### 3.5 No Community and Governance Files

| File | Why It Is Needed |
|---|---|
| `CONTRIBUTING.md` | Describes the contribution workflow and the **CLA requirement** |
| `CODE_OF_CONDUCT.md` | Sets community behaviour expectations (Contributor Covenant 2.1 recommended) |
| `SECURITY.md` | Provides a responsible-disclosure contact and expected response process |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Guides bug reporters to provide useful information |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Guides feature requesters |
| `.github/pull_request_template.md` | Ensures PRs include necessary context and checklist |

---

## 4. Risks

| Risk | Severity | Impact |
|---|---|---|
| AGPL-3.0 badge on a BUSL-1.1 codebase | **High** | Legal confusion; enterprise customers may reject the product; contributors may believe they have rights they do not have |
| "Open source" badge on a source-available codebase | **High** | Misrepresents the licensing model; undermines commercial viability |
| No `LICENSE` file | **High** | Legally ambiguous; no enforceable terms; potential IP disputes |
| Code committed without `.gitignore` | **Medium** | Secrets or large binaries may end up in git history; difficult and embarrassing to purge |
| No CLA before accepting PRs | **Medium** | Contributions without a CLA complicate future re-licensing or commercialisation |
| No `SECURITY.md` | **Low–Medium** | Security researchers have no clear disclosure path; may lead to public disclosure without warning |

---

## 5. Pre-Implementation Checklist

All items below must be completed and merged to the main branch **before any
application code is written**. This is a hard gate.

```
[ ] 1.  Replace AGPL-3.0 badge in README.md with a "Source Available — BUSL-1.1" badge
[ ] 2.  Remove or replace the "open-source" badge in README.md
[ ] 3.  Add a plain-text license notice to README.md:
            "Servario is source-available under the Business Source License 1.1.
             Production use requires a license. See LICENSE for details."
[ ] 4.  Create LICENSE file (BUSL-1.1) with all fields filled in (see §3.2 above)
[ ] 5.  Create .gitignore covering:
            - Python (venv/, __pycache__/, *.pyc, .env, .env.*)
            - Node.js (node_modules/, .next/, dist/)
            - Docker (.env, *.override.yml)
            - OS artefacts (.DS_Store, Thumbs.db)
            - IDE config (.idea/, .vscode/)
[ ] 6.  Create CONTRIBUTING.md including:
            - How to open issues and submit pull requests
            - CLA requirement (text to be defined — see decision E9 in PLAN.md)
            - Code style and linting expectations
            - Branch naming conventions
[ ] 7.  Create CODE_OF_CONDUCT.md (Contributor Covenant 2.1 recommended)
[ ] 8.  Create SECURITY.md with:
            - Responsible disclosure e-mail / process
            - Supported versions table
            - Expected response time commitment
[ ] 9.  Create .github/ISSUE_TEMPLATE/bug_report.yml
[ ] 10. Create .github/ISSUE_TEMPLATE/feature_request.yml
[ ] 11. Create .github/pull_request_template.md
[ ] 12. Create docker-compose.yml skeleton
            (services: api, frontend, db, proxy)
[ ] 13. Create .env.example with all required environment variable keys
            (values empty or annotated with descriptions; never committed with real secrets)
[ ] 14. Confirm open decisions E7, E9, E10, E11, E12 (see PLAN.md) before writing any code
            that touches the license, billing, or authentication subsystems
```

---

## 6. Definition of "Repository Ready"

The repository is considered **ready for implementation** when:

1. All 14 checklist items above are complete and merged to the main branch.
2. All open decisions in `PLAN.md` that block Phase 0 or Phase 1 are resolved.
3. The `main` branch reflects the corrected license badges, a valid `LICENSE` file,
   a proper `.gitignore`, and all community health files.

See [10_next_steps.md](./10_next_steps.md) for the full implementation phase plan.
