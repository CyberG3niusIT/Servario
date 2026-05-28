# Servario — Multi-Agent Design Review

**Document status:** Draft
**Last updated:** 2026-05-28
**Audience:** Core team and future contributors who need to understand why key decisions were made

This document records the structured multi-agent design review for the Servario project. Each agent represents a distinct domain perspective. Positions, vetoes, and consensus outcomes are recorded verbatim so that future contributors can trace the reasoning behind architectural decisions.

---

## Agents

| # | Role | Domain | Key concern |
|---|---|---|---|
| 1 | Product Architect | Product scope and vision | Ensures features serve the target user; owns the MVP boundary |
| 2 | Repository & Community Maintainer | Source availability, contribution model | Sets contribution norms; manages the distinction between source-available and open source |
| 3 | Backend Architect | Python/FastAPI, PostgreSQL, API design | Correctness, performance, and maintainability of the server layer |
| 4 | Frontend / UX Architect | Next.js, public booking page, admin dashboard | Usability for non-technical business owners and mobile-first customers |
| 5 | Security & Privacy Reviewer | Data handling, license validation, threat model | Privacy by design; ensures no data leakage in license validation |
| 6 | DevOps / Selfhosting Architect | Docker Compose, Nginx Proxy Manager, deployment | Reliable, reproducible self-hosted deployments with minimal ops burden |
| 7 | QA / Test Architect | Test strategy, acceptance criteria, CI | Confidence in release quality; catches regressions before they reach users |
| 8 | Documentation & README Designer | README, user-facing docs, onboarding | Honest, accurate documentation that sets correct expectations |
| 9 | Licensing & Commercial Model Reviewer | License compliance, commercial model integrity | **Holds veto power** over any license designation or commercial model decision |
| 10 | RevenueCat Licensing Architect | Billing integration, license document flow | Ensures billing and validation are architecturally separated |

---

## Round 1: License Fundamentals

### Position — Licensing & Commercial Model Reviewer (Agent 9)

The project cannot use AGPL-3.0 as its license. This is not a preference — it is a hard incompatibility.

**Why AGPL-3.0 is incompatible:**

AGPL-3.0 is an OSI-approved open source license. Section 10 of the AGPL explicitly prohibits imposing additional restrictions on the rights granted by the license. The right to use the software — including in production, commercially, and without payment — is a core freedom granted by any OSI open source license. No additional restriction (such as "production use requires payment") can be layered on top of AGPL-3.0 without violating the license itself.

Some projects have historically adopted AGPL-3.0 to address the "SaaS loophole" — the concern that a cloud provider could deploy the software as a service without contributing modifications back. However:

1. The SaaS loophole concern is irrelevant here because Servario's model requires **all** production use (including self-hosted) to hold a license. AGPL-3.0 does not enable this; it prohibits it.
2. Any attempt to enforce payment for production use of AGPL-3.0 software would be legally unenforceable and would expose the project to significant legal risk.

**Recommended alternatives reviewed:**

| License | Assessment |
|---|---|
| AGPL-3.0 | Incompatible — grants free production use |
| GPL-3.0 | Incompatible — grants free production use |
| MIT / Apache 2.0 | Incompatible — grants free production use and sublicensing |
| ELv2 (Elastic License 2.0) | Compatible — prohibits SaaS and competing managed services; no production-use payment requirement |
| BUSL-1.1 (Business Source License 1.1) | **Recommended** — see below |
| Custom source-available | Compatible but creates legal uncertainty and contributor friction |

**Recommendation: BUSL-1.1**

BUSL-1.1 is the preferred license for the following reasons:

- It is a standardized, well-understood license used by production projects (MariaDB, HashiCorp pre-fork, Sentry, and others)
- It explicitly requires a commercial license for "production use" as defined by the licensor
- Each file's "Change Date" triggers automatic conversion to Apache 2.0 after four years, providing a long-term commitment to eventual openness that builds community trust
- No Contributor License Agreement (CLA) is required by the license itself, though contributors to Servario will still sign a project CLA to protect the project's ability to re-license or enforce the BUSL terms
- The license text is short and readable; contributors and self-hosters can understand it without legal counsel

---

### VETO — Licensing & Commercial Model Reviewer (Agent 9)

> **VETO ISSUED:**
>
> No planning document, badge, README section, code comment, changelog entry, marketing material, or any other artifact associated with the Servario project may reference AGPL-3.0 as the license for Servario application software.
>
> Any existing reference to AGPL-3.0 in project files must be replaced with the finalized license designation (BUSL-1.1) or the phrase "Source Available — see LICENSE" until the LICENSE file is finalized.
>
> This veto applies retroactively to all documents in this repository.

**VETO ACCEPTED.** All agents acknowledge. The license for Servario application software is **BUSL-1.1**. AGPL-3.0 does not appear in any project artifact.

---

### Position — RevenueCat Licensing Architect (Agent 10)

The billing and license validation layers must be strictly separated. This has architectural consequences that must be established before any backend design begins.

**What RevenueCat is and is not:**

RevenueCat is a subscription and entitlement management service. It handles payment processing (via app stores and payment processors), subscription lifecycle events (trial, renewal, cancellation, refund), and entitlement assignment. It is the **billing layer**.

RevenueCat is **not** a license validator. It does not issue the license documents that Servario instances verify. Treating RevenueCat as the validator would require Servario instances to call RevenueCat directly, which would expose RevenueCat API keys to self-hosted deployments — a critical security failure.

**Architecture:**

```
Customer payment
       ↓
   RevenueCat
   (billing, entitlement management)
       ↓
  License Broker
  (private, separately deployed service)
  Receives RevenueCat webhooks
  Issues Ed25519-signed license documents
       ↓
  Ed25519-signed license document
  (downloaded by the Servario instance; stored locally)
       ↓
  Servario instance
  (verifies Ed25519 signature using embedded public key;
   no RevenueCat API call; no network dependency for validation)
```

**Key security properties of this architecture:**

- RevenueCat secret keys, webhook secrets, and API credentials **never exist** in the self-hosted Servario codebase, configuration, or environment. They exist only in the License Broker.
- The License Broker is a private service not distributed as part of Servario. It is operated by the Servario project team.
- License validation in Servario is purely cryptographic: verify the Ed25519 signature on the license document using the embedded public key. No network call required for validation.
- Online validation (optional in MVP) is used only for freshness checks — detecting revocations faster than waiting for license expiry. It transmits only: `license_id`, `instance_id` (locally generated UUID), `version`, and optionally `domain`. No booking data, customer data, or personal information is transmitted.

**Entitlement mapping:**

The License Broker maps RevenueCat entitlement identifiers to Servario edition names in the signed license document:

| RevenueCat entitlement ID | Servario edition in license document |
|---|---|
| `servario_starter` | `starter` |
| `servario_professional` | `professional` |
| `servario_business` | `business` |

**Demo/Eval mode is not a RevenueCat product:**

Demo/Eval mode is a license-less operating mode built into Servario. It has no corresponding RevenueCat entitlement, no license document, and no License Broker interaction. It is purely enforced in Servario application code based on the absence of a valid license.

---

## Round 2: Impact on Other Agents

### Product Architect (Agent 1)

The license module is a first-class MVP component, not a post-MVP concern. It must be designed and built alongside the core booking functionality.

**Implications for MVP scope:**

- License checking must occur at application startup. The HTTP server must not accept production booking requests until the license module has loaded and evaluated the license state.
- Demo mode limits are product UX, not just enforcement code. The admin must see clear, friendly messaging when approaching limits (e.g., "4 of 5 demo bookings used") and a clear call-to-action when a limit is reached.
- The license status widget in the admin dashboard is an MVP requirement, not a nice-to-have.

**Hard limits for Demo/Eval mode (confirmed):**

| Limit | Value | Enforcement |
|---|---|---|
| Maximum total bookings | 5 | Block booking creation at limit |
| Maximum staff accounts | 2 | Block staff creation at limit |
| Maximum services | 3 | Block service creation at limit |
| Maximum operating window | 30 days from first startup | Block all bookings after window expires |

All four limits are independent. Reaching any one of them blocks the corresponding action regardless of the state of the others.

---

### Security & Privacy Reviewer (Agent 5)

Three security properties are non-negotiable and must be encoded in the architecture from day one.

**1. No hardware fingerprinting**

The license validation system must not attempt to bind a license to hardware characteristics (CPU serial, MAC address, disk serial, etc.). Hardware fingerprinting:

- Breaks legitimate deployments when hardware is replaced or virtualized
- Raises significant privacy concerns for self-hosters
- Is trivially bypassed, providing no meaningful protection

The `instance_id` used in optional online validation is a **locally generated UUID** stored in the database or configuration. It is not derived from hardware.

**2. Privacy-minimal online validation**

If online validation is implemented in MVP, the request payload must contain only:

```json
{
  "license_id": "<opaque identifier from license document>",
  "instance_id": "<locally generated UUID>",
  "version": "<Servario version string>",
  "domain": "<optional, admin-configured>"
}
```

No booking counts, customer emails, staff names, service names, or any data from the booking system may be included in license validation requests. This is a GDPR concern as well as a trust concern.

**3. `invalid` license status must not fall back to Demo/Eval mode**

This is the most important security property of the license enforcement model.

When a license is `missing` (never been configured), Demo/Eval mode is appropriate — the instance is newly installed and the operator is evaluating the product.

When a license is `invalid` (present but failing signature verification, expired, or explicitly revoked), this is a distinct security signal. An invalid license may indicate:

- A forged or tampered license document
- A revoked license (e.g., due to chargebacks or terms violations)
- A replay attack using a previously valid license from a different instance
- A downgrade attack attempting to bypass edition limits

Falling back to Demo mode on an invalid license would allow an attacker to downgrade a fully licensed instance to Demo mode by invalidating the license, then re-operate the instance within Demo limits indefinitely. **The correct behavior on `invalid` is: block new bookings, keep admin access and data export available, and require the operator to contact support or re-enter a valid license key.**

---

### DevOps / Selfhosting Architect (Agent 6)

License configuration must be handled through environment variables in the standard Docker Compose deployment. The following variables are required in `.env.example`:

```bash
# License configuration
SERVARIO_LICENSE_KEY=           # The license key obtained at purchase; leave empty for demo mode
SERVARIO_INSTANCE_ID=           # Auto-generated on first start; do NOT change after initial setup
SERVARIO_LICENSE_SERVER_URL=    # URL of the license validation server (provided by Servario)
SERVARIO_LICENSE_OFFLINE_GRACE_DAYS=30  # Days of operation allowed without successful online validation

# RevenueCat keys: DO NOT ADD THESE HERE
# RevenueCat API keys, webhook secrets, and app secrets are NOT used by the
# self-hosted Servario instance. They exist only in the License Broker service.
# If you have been told to add RevenueCat keys here, that is incorrect.
```

The `SERVARIO_INSTANCE_ID` must be generated once on first startup and persisted. The Docker Compose volume configuration must ensure this value survives container restarts and upgrades.

No RevenueCat API keys, webhook secrets, or credentials of any kind appear in `.env.example` or any Servario configuration file.

---

### Repository & Community Maintainer (Agent 2)

The project's public presence must accurately reflect its source-available, non-open-source status. This has specific implications:

**Contribution model:**

- Contributors must sign a Contributor License Agreement (CLA) before patches are merged. This is required to preserve the project's ability to enforce BUSL-1.1 terms and to issue commercial licenses.
- [ASSUMPTION] A CLA bot (e.g., CLA Assistant) will be configured on the repository to automate CLA checking on pull requests.

**OSI badges and language:**

- No OSI "Open Source" badge in the README or repository metadata
- No "open-source project" language in the README, description, or website
- The repository's license field must be set to `BUSL-1.1`, not any OSI-approved identifier
- The project description is: "Source-available appointment and booking platform" — not "open-source"

**Community tone:**

- The project welcomes issues, bug reports, and feature requests from the community
- External contributions are welcomed with the understanding that a CLA is required
- The distinction between "source available" and "open source" must be explained clearly in the CONTRIBUTING.md document

---

## Consolidated Consensus

The following positions were debated and reached consensus across all ten agents. Dissenting notes, where they exist, are recorded.

| Topic | Decision | Notes |
|---|---|---|
| **AGPL-3.0 removed** | Confirmed — AGPL-3.0 is not the license for any Servario software | Veto issued and accepted in Round 1 |
| **License model** | BUSL-1.1 | Standardized, production-proven, converts to Apache 2.0 after 4 years |
| **License enforcement** | Ed25519-signed license documents | Public key embedded in Servario binary; no RevenueCat call from instance |
| **No hardware fingerprints** | Confirmed | Instance ID is a locally generated UUID; no hardware binding |
| **Online validation** | Optional in MVP; privacy-minimal payload | Only license_id, instance_id, version, optional domain |
| **Offline grace period** | 30 days default, configurable via `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` | Allows operation during network outages or license server downtime |
| **Demo mode limits** | 5 bookings / 2 staff / 3 services / 30 days | Hard limits; not configurable by the operator |
| **`invalid` ≠ Demo fallback** | Confirmed | Invalid license blocks new bookings; admin access and data export remain |
| **`missing` → Demo/Eval** | Confirmed | Missing license permits Demo/Eval mode until a limit is reached |
| **CLA required** | Confirmed | All external contributors must sign CLA before patches are merged |
| **No OSI badges** | Confirmed | Project is source-available, not OSI open source |
| **RevenueCat as billing layer only** | Confirmed | RevenueCat is not called by self-hosted Servario instances |
| **RevenueCat secrets in License Broker only** | Confirmed | No RevenueCat credentials in Servario codebase or `.env.example` |
| **Editions** | Starter / Professional / Business | No "Community" edition |
| **Single-org model** | Confirmed | No `org_id` in domain tables; one instance per organization |

---

## Open Questions

The following questions were identified during the debate but not resolved in this document. They are tracked as items E1–E12 in `PLAN.md`.

- **E1** — Edition feature matrix: What specific features differentiate Starter, Professional, and Business editions? [ASSUMPTION] Likely: staff count limits, service count limits, advanced notification features, custom branding.
- **E2** — CLA tooling: Which CLA tool will be used? CLA Assistant, Contributor Covenant variant, or custom?
- **E3** — License Broker architecture: Where is the License Broker deployed? What SLA is required for license issuance?
- **E4** — Offline grace period behavior: After the grace period expires on an instance with a `valid` license that cannot reach the validation server, does behavior match `invalid` or `expired`?
- **E5** — License renewal flow: What is the UX for renewing an expired license without downtime?
- **E6** — Demo limit reset: Can Demo/Eval limits be reset (e.g., by wiping the database)? Is this intended or a gap?
- **E7** — BUSL-1.1 Change Date: What is the specific Change Date for the initial release? Four years from first public release is standard.
- **E8** — NOTICE file: What third-party dependencies require attribution in the NOTICE file?
- **E9** — Optional domain field in validation: Is the domain field opt-in (admin configures it) or opt-out (included by default, admin can suppress)?
- **E10** — RevenueCat entitlement IDs: Are `servario_starter`, `servario_professional`, `servario_business` the finalized entitlement identifiers?
- **E11** — License document schema: What fields are included in the signed license document? (license_id, instance_id, edition, issued_at, valid_until, domain?, public_key?)
- **E12** — Contribution flow for security vulnerabilities: Is there a private security disclosure channel? What is the embargo policy?
