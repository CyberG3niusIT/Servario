# 11 — License Model

**Project:** Servario — Self-Hosted, Source-Available Appointment / Service / Booking Platform
**Document status:** Authoritative planning document
**Last updated:** 2026-05-28

---

## Table of Contents

1. [Terminology](#1-terminology)
2. [Why AGPL-3.0 Is Incompatible with Servario's Model](#2-why-agpl-30-is-incompatible)
3. [License Model Options with Evaluation](#3-license-model-options-with-evaluation)
4. [Recommendation: BUSL-1.1](#4-recommendation-busl-11)
5. [License Validation Architecture](#5-license-validation-architecture)
6. [RevenueCat Billing Integration](#6-revenuecat-billing-integration)
7. [Privacy Assessment](#7-privacy-assessment)
8. [Risks and Limits of Technical License Enforcement](#8-risks-and-limits-of-technical-license-enforcement)
9. [MVP Requirements — License System](#9-mvp-requirements--license-system)
10. [Post-MVP Extensions](#10-post-mvp-extensions)
11. [Appendix: Environment Variable Reference](#appendix-environment-variable-reference)

---

## 1. Terminology

The following terms are frequently confused in the industry. This document uses them with precise, consistent meanings.

### Open Source (OSI Definition)

A license is Open Source if and only if it satisfies all ten criteria of the [Open Source Definition](https://opensource.org/osd) maintained by the Open Source Initiative (OSI). The most operationally relevant criteria for this document are:

- **Free redistribution** — the license may not restrict anyone from selling or giving away the software.
- **No discrimination against persons, groups, or fields of endeavor** — the license may not restrict use in any industry or for any purpose, including commercial production use.
- **No additional restrictions** — the license may not place any restrictions on other rights granted by the license.

**Servario is NOT Open Source.** An Open Source license unconditionally grants production use to every recipient at no charge. Requiring a paid commercial license for production use is by definition incompatible with the OSI definition. Any claim that Servario is "open source" is factually incorrect and must be avoided in all communications, marketing copy, and documentation.

### Source Available / Shared Source

Source code is publicly visible (typically on a public repository), but the license restricts certain uses — most commonly commercial or production use — and may require a separate agreement or payment for those uses.

**Servario IS source available.** The source code is published for transparency, developer evaluation, and non-production use. Production use requires a commercial license from the licensor. This model is sometimes called "shared source" and is used by numerous commercial software companies.

### Proprietary

Source code is not published. Users receive compiled binaries or SaaS access only. No inspection, modification, or redistribution is permitted. Servario is explicitly **not** proprietary; source visibility is a deliberate design and trust decision.

### Open Core

A hybrid model: a subset of functionality (the "community edition" or "core") is distributed under a genuine Open Source license and is free to use in production without restriction. A separate tier with additional features is distributed under a proprietary or commercial license. **Servario does not use an Open Core model.** There is no free-production-use community tier. All production use of Servario, regardless of feature set, requires a paid license.

> [ASSUMPTION] This decision is intentional. If a future community/free tier is introduced, this entire document must be re-evaluated because the license structure would shift to Open Core.

### Dual-Licensing

The same codebase is simultaneously available under two licenses: (1) a copyleft Open Source license (typically AGPL or GPL) and (2) a proprietary commercial license. Recipients who can comply with the copyleft terms use the Open Source license for free; recipients who cannot comply (e.g., they do not want to release their derivative source) pay for the commercial license. This model is used by companies such as MySQL/MariaDB and Qt. **Servario does not use dual-licensing** for reasons detailed in Section 3.

### Commercial License

A bespoke grant of usage rights issued directly by the copyright holder to a specific customer, in exchange for payment. The commercial license supersedes and replaces the source-available license for that customer, granting rights that the public license withholds (specifically: production use). In Servario's model, every production instance must hold a valid commercial license issued by the licensor via the License Broker system.

---

## 2. Why AGPL-3.0 Is Incompatible

AGPL-3.0 is sometimes incorrectly cited as Servario's license. This section explains why AGPL-3.0 is fundamentally incompatible with Servario's commercial model and must not be used.

### AGPL-3.0 Grants Unconditional Production Use

The GNU Affero General Public License, Version 3 (AGPL-3.0) is an Open Source license that meets all OSI criteria. By receiving AGPL-3.0-licensed software, any party obtains the unconditional right to:

- Run the software for any purpose, including commercial production use, at no charge.
- Modify the software.
- Distribute copies and modifications, provided they also carry AGPL-3.0.

No payment can be required as a condition of production use under AGPL-3.0. This is not a technicality — it is a core design property of the license.

### AGPL Section 10 Prohibits Additional Restrictions

AGPL-3.0 Section 10 states:

> "You may not impose any further restrictions on the exercise of the rights granted or affirmed under this License."

A requirement that production users pay for a commercial license is precisely such an "additional restriction." Any operator who receives Servario under AGPL-3.0 could legally challenge the commercial license requirement as void under the terms of the license they received. The licensor would have no enforceable claim against a user who relied solely on the AGPL-3.0 terms.

### The SaaS Loophole Motivation Is Irrelevant

The AGPL was designed to close the "SaaS loophole": a company could use GPL software to run a network service without distributing the software, thus never triggering GPL's share-alike obligation. AGPL closes this by requiring source disclosure even for network-delivered software.

This motivation is irrelevant to Servario because **all production use — whether SaaS, self-hosted, or any other deployment form — requires a paid license**. The distinction between SaaS and self-hosted that AGPL was designed to address does not map onto Servario's commercial model.

### Conclusion

AGPL-3.0 must not be used as Servario's license. Any file, README, or documentation that states AGPL-3.0 as the Servario license is incorrect and must be updated. Any reference to AGPL-3.0 in the codebase must be treated as an error to be resolved before any public release.

---

## 3. License Model Options with Evaluation

### Option A: Custom Source-Available License

**Description:** A bespoke license document drafted specifically for Servario, granting source visibility and non-production use, and requiring a commercial license for production use. Used by some early-stage commercial open-source companies.

**Advantages:**
- Full control over every clause; no terms imposed by a third-party license template.
- No mandatory change date or future obligation to relicense.
- Can be precisely tailored to Servario's exact use case and enforcement preferences.

**Disadvantages:**
- Unfamiliar to developers evaluating the project; non-standard licenses create friction and distrust.
- Unfamiliar to legal teams at potential enterprise customers; increases sales friction.
- Requires qualified legal counsel to draft and maintain; significant cost.
- Not recognized by SPDX; no standard identifier; poor GitHub/tooling integration.
- Community friction: perceived as a "made-up license" with unpredictable terms.
- No established case law or industry precedent for enforcement.

**Verdict:** Viable but suboptimal. Should only be chosen if standardized options are genuinely insufficient.

---

### Option B: Business Source License 1.1 (BUSL-1.1)

**Description:** Developed by MariaDB, the Business Source License (BUSL-1.1) is a source-available license that:

- Permits all non-production use (development, testing, CI, evaluation) without a commercial license.
- Requires a commercial license from the licensor for any production use.
- Contains a mandatory **Change Date**: on a specified date (typically four years after a release), the license automatically converts to a designated Open Source license (typically Apache 2.0).

**SPDX identifier:** `BUSL-1.1` — recognized by GitHub, FOSSA, and standard dependency scanners.

**Notable adopters:** HashiCorp Terraform (pre-OpenTofu fork), CockroachDB, MariaDB, Couchbase.

**Advantages:**
- Standardized, widely recognized, well-understood by developers and legal teams.
- Directly addresses the commercial requirement: production use explicitly requires a commercial license.
- The Change Date creates a goodwill signal: the software will eventually be fully open source.
- No Contributor License Agreement (CLA) required from contributors for the license itself to function (though a CLA or DCO is still advisable for contribution hygiene).
- No ambiguity about copyleft obligations: contributors do not need to assess GPL compatibility.
- Good GitHub integration: SPDX identifier renders correctly in repository metadata.

**Disadvantages:**
- The Change Date requires release management discipline: each major release should have a defined Change Date, and those dates must be tracked.
- The future Apache 2.0 conversion means the licensor loses commercial control over old versions after the Change Date. This is a feature for community trust but a business consideration.
- The licensor must clearly define what constitutes "production use" to avoid ambiguity.

**Verdict:** Recommended. See Section 4.

---

### Option C: Elastic License 2.0 (ELv2)

**Description:** Developed by Elastic (Elasticsearch), ELv2 permits all use of the software except two prohibited activities:

1. **Managed service provision:** Using the software to provide a managed service to third parties — i.e., operating it as SaaS where the primary value to the customer is the software's functionality.
2. **Circumventing license key mechanisms:** Modifying, disabling, or circumventing any feature that is controlled by a license key.

**Notable adopters:** Elasticsearch, Kibana, Logstash.

**Advantages:**
- Simple, readable two-prohibition model.
- No time-based conversion.
- Well-regarded by the developer community as a fair compromise.

**Disadvantages:**
- ELv2 does **not** inherently require payment for self-hosted production use. It prohibits SaaS resale and circumvention, but an operator running Servario for their own business on their own infrastructure is **permitted** under ELv2 without any payment.
- To add a payment requirement for self-hosted production use, ELv2 would need to be customized — but modifying a named license creates a custom license, negating the standardization benefit.
- Does not meet Servario's core requirement that **all** production use requires a paid commercial license.

**Verdict:** Not suitable for Servario without modification, which would make it a custom license. Not recommended.

---

### Option D: Dual-Licensing (AGPL-3.0 + Commercial)

**Description:** The codebase is published under AGPL-3.0. Users who can accept AGPL-3.0's copyleft terms (primarily: disclosing their modifications and keeping the license intact) may use it for free, including in production. Users who cannot comply with AGPL-3.0 (e.g., they wish to embed Servario in proprietary software) purchase a commercial license.

**Notable adopters:** Qt (GPL + commercial), MySQL (GPL + commercial), Nextcloud (AGPL + commercial for enterprise extensions).

**Advantages:**
- Well-understood model; extensive precedent.
- Generates commercial license revenue from corporate users who cannot comply with copyleft.

**Disadvantages:**
- **Fatal for Servario's model:** Self-hosted operators who are willing to comply with AGPL-3.0 (accepting that their modifications must be disclosed under AGPL) owe nothing and can use Servario in production for free. This directly contradicts the business requirement that all production use requires a paid license.
- Requires a Contributor License Agreement (CLA) from all contributors to allow the licensor to issue commercial licenses. This is an administrative and community friction burden.
- The commercial license value proposition becomes narrow: only those who specifically cannot comply with copyleft need to pay.

**Verdict:** Does not meet Servario's requirement that all production use requires a paid license. Must not be used.

---

## 4. Recommendation: BUSL-1.1

**BUSL-1.1 is the recommended license for Servario.**

### Justification

BUSL-1.1 is the only standardized, community-recognized license that:

1. Makes all production use contingent on a commercial license from the licensor.
2. Allows free non-production use (development, testing, CI, evaluation), enabling developers to evaluate and integrate the software.
3. Provides a long-term open source conversion path via the Change Date, building community trust.
4. Does not require a CLA from contributors for the license to function.
5. Is recognized by SPDX and integrates cleanly with GitHub, package scanners, and legal review tooling.
6. Has established precedent from large-scale commercial deployments.

### BUSL-1.1 Configuration for Servario

The following parameters must be set in the `LICENSE` file at the repository root. Parameters marked [ASSUMPTION] require a decision before the first public release.

| BUSL-1.1 Field | Servario Value |
|---|---|
| **Licensor** | [ASSUMPTION] Legal name of the individual developer or registered legal entity — must be determined and filled before first public release. |
| **Licensed Work** | Servario |
| **Additional Use Grant** | "Use in non-production environments (development, testing, continuous integration, and evaluation) is permitted without a commercial license." |
| **Change Date** | Four years from the release date of each major version (e.g., v1.0.0 Change Date: 2030-XX-XX). [ASSUMPTION] Exact process for tracking per-version Change Dates must be established. |
| **Change License** | Apache License, Version 2.0 |

### What This Means in Practice

| Use case | License required? |
|---|---|
| Running Servario on a local machine for development | No |
| Running Servario in a CI/CD pipeline to test integrations | No |
| Evaluating Servario before purchasing a license | No |
| Running Servario in production for any business, organization, or individual | **Yes — commercial license required** |
| Operating Servario as a managed/hosted service for third parties | **Yes — commercial license required** |
| Distributing a modified fork for non-production use | Permitted under BUSL-1.1 terms |
| Versions older than their Change Date, after the Change Date passes | Apache 2.0 applies; production use permitted without commercial license |

---

## 5. License Validation Architecture

### License Data Model

Each issued license is a signed JSON document. The following fields constitute the canonical schema.

```json
{
  "license_id":             "UUID",
  "customer_reference":     "VARCHAR",
  "instance_id":            "VARCHAR",
  "edition":                "starter | professional | business",
  "allowed_features":       ["feature_flag_a", "feature_flag_b"],
  "max_staff":              -1,
  "max_services":           -1,
  "max_bookings_per_month": null,
  "issued_at":              "2026-01-15T10:00:00Z",
  "expires_at":             null,
  "last_validated_at":      "2026-05-28T08:00:00Z",
  "grace_until":            "2026-06-27T08:00:00Z",
  "signature":              "<Ed25519 signature — base64url encoded>"
}
```

**Field definitions:**

| Field | Type | Description |
|---|---|---|
| `license_id` | UUID | Globally unique identifier; issued by the License Broker. Used for revocation checks. |
| `customer_reference` | VARCHAR | Opaque reference string. Not personal data within the application; maps to a customer record in the License Broker's private system. |
| `instance_id` | VARCHAR | UUID generated locally on first start; identifies this installation. No hardware binding. |
| `edition` | ENUM | One of: `starter`, `professional`, `business`. The value `community` is **not valid** and must never appear. |
| `allowed_features` | JSON Array | List of feature flag strings that are enabled for this license. Signature-protected; tampering invalidates the license. |
| `max_staff` | INTEGER | Maximum number of staff members. `-1` means unlimited. |
| `max_services` | INTEGER | Maximum number of services. `-1` means unlimited. |
| `max_bookings_per_month` | INTEGER | Optional monthly booking throttle. `null` means no limit. |
| `issued_at` | TIMESTAMPTZ | UTC timestamp of issuance. |
| `expires_at` | TIMESTAMPTZ | Expiry timestamp, UTC. `null` means perpetual (no expiry). |
| `last_validated_at` | TIMESTAMPTZ | Updated on each successful online validation with the License Broker. |
| `grace_until` | TIMESTAMPTZ | Deadline for online validation; operations continue in grace mode until this timestamp if the License Broker is unreachable. |
| `signature` | VARCHAR | Ed25519 signature (base64url) over the canonical payload. Canonical payload = JSON with all fields except `signature`, keys sorted lexicographically, no extra whitespace. |
| `license_status` | ENUM | Runtime-computed status field. See status enum below. Not included in the signed payload; computed by the application at validation time. |

> **Note:** `"community"` is NOT a valid value for `edition`. Demo/Eval is an operating mode for unlicensed instances, not an edition in a license document. No license document for the Demo/Eval mode exists or is issued.

---

### License Status Enum

| Value | Meaning |
|---|---|
| `missing` | No license file found and no `SERVARIO_LICENSE_KEY` env var set. Demo/Eval mode is permitted until Demo limits are reached. |
| `invalid` | License document is present but Ed25519 signature verification failed, or the document is malformed (unparseable JSON, missing required fields). **No Demo/Eval fallback.** |
| `active` | License is valid, within expiry (or non-expiring), and online validation is current. Normal operation. |
| `expired` | `expires_at` is in the past AND the grace period (`grace_until`) has also elapsed. New bookings blocked. |
| `grace` | Online validation is temporarily unavailable but within the `grace_until` window, OR `expires_at` is in the past but within `grace_until`. Operations continue with a visible warning. |
| `revoked` | The License Broker has marked this `license_id` as revoked. New bookings blocked; admin access and data export remain available. |
| `server_unreachable` | Intermediate technical state: License Broker could not be contacted during background validation. Resolved to `grace` if within `grace_until`, otherwise treated as `expired`. |

---

### Booking Restriction Decision Matrix

| License Status | New Bookings | Admin Access | Data Export |
|---|---|---|---|
| `active` | Allowed | Yes | Yes |
| `grace` | Allowed (warning banner shown) | Yes | Yes |
| `server_unreachable` (within `grace_until`) | Allowed (warning shown) | Yes | Yes |
| `server_unreachable` (grace elapsed) | Blocked | Yes | Yes |
| `missing` — demo limits not yet reached | Allowed (demo banner shown in all UI views) | Yes | Yes |
| `missing` — demo limits reached | Blocked; admin prompted to acquire license | Yes | Yes |
| `expired` (within `grace_until`) | Allowed (warning shown) | Yes | Yes |
| `expired` (grace elapsed) | Blocked | Yes | Yes |
| `invalid` | Blocked — **no Demo/Eval fallback** | Yes | Yes |
| `revoked` | Blocked | Yes | Yes |

> **Data access principle:** Under no status is existing customer or booking data made inaccessible. Expiry, revocation, and invalidity block new bookings and configurations; they do not lock administrators out of their own data. This is an explicit design decision to prevent data hostage situations.

---

### Signature Scheme: Ed25519

**Algorithm:** Ed25519 (Edwards-curve Digital Signature Algorithm, Curve25519)

**Key management:**

| Key | Location | Access |
|---|---|---|
| Ed25519 private key | License Broker — private system, **never** in the public repository | License Broker operator only |
| Ed25519 public key | Compiled into the Servario backend at build time | Public; no secret |

**Implementation:** Use `PyNaCl` (`nacl.signing.VerifyKey`) or the `cryptography` library (`cryptography.hazmat.primitives.asymmetric.ed25519`). No custom cryptographic implementation. No home-grown signing or verification logic.

**Canonical payload construction:**

```python
import json

def canonical_payload(license_doc: dict) -> bytes:
    """
    Produce the canonical byte sequence for Ed25519 signing/verification.
    All fields except 'signature' are included.
    Keys are sorted lexicographically. No extra whitespace.
    """
    payload = {k: v for k, v in license_doc.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
```

**Verification pseudocode:**

```python
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import base64

SERVARIO_PUBLIC_KEY_B64 = "<compiled-in base64url public key>"

def verify_license(license_doc: dict) -> bool:
    try:
        vk = VerifyKey(base64.urlsafe_b64decode(SERVARIO_PUBLIC_KEY_B64 + "=="))
        payload = canonical_payload(license_doc)
        sig = base64.urlsafe_b64decode(license_doc["signature"] + "==")
        vk.verify(payload, sig)
        return True
    except (BadSignatureError, KeyError, ValueError):
        return False
```

---

### Validation Flow at Startup

```
STARTUP LICENSE VALIDATION SEQUENCE
=====================================

Step 1 — Read license
  ├─ Check SERVARIO_LICENSE_KEY environment variable (base64-encoded signed JSON)
  ├─ If not set: check /data/license.json
  └─ If neither found:
       → status = missing
       → Proceed in Demo/Eval mode if demo eligibility limits not exceeded
       → STOP (no further validation)

Step 2 — Parse and verify signature
  ├─ Attempt JSON parse of license document
  ├─ Check all required fields are present
  ├─ Verify Ed25519 signature against compiled-in public key
  └─ If any check fails:
       → status = invalid
       → Block new bookings; NO Demo/Eval fallback
       → Show actionable error in admin dashboard
       → Admin may remove the invalid license file to return to Demo/Eval mode
         (if instance is still within demo eligibility)

Step 3 — Check expiry
  ├─ If expires_at is null: no expiry; continue
  ├─ If expires_at is in the past AND now > grace_until:
  │    → status = expired → block new bookings
  └─ If expires_at is in the past AND now <= grace_until:
       → status = grace → warn and continue

Step 4 — Check revocation status in document
  └─ If license_status field == "revoked":
       → status = revoked → block new bookings

Step 5 — License locally valid
  → status = active (tentative, pending background online validation)
  → Normal operation begins

Step 6 — Background online validation (every 24 hours)
  ├─ POST to SERVARIO_LICENSE_SERVER_URL/api/v1/license/validate
  │    Payload: { license_id, instance_id, version, domain (optional) }
  ├─ On success:
  │    → Update last_validated_at, grace_until, status from response
  ├─ On server unreachable / timeout / network error:
  │    → status = server_unreachable
  │    → If now <= grace_until: treat as grace (warn, continue)
  │    → If now > grace_until: block new bookings
  └─ On revocation response:
       → status = revoked → block new bookings
```

---

### Grace Period

The grace period allows a Servario instance to continue operating when the License Broker is temporarily unreachable (network outage, maintenance, etc.).

- **Default:** 30 days after the last successful online validation.
- **Configuration:** `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` environment variable.
  - Default: `30`
  - Minimum: `1`
  - Maximum: `90`
- The `grace_until` timestamp is updated by the License Broker on every successful validation and included in the license document or validation response.

---

### Demo / Eval Mode

Demo/Eval mode activates when no license is present (`status = missing`) and the instance is within all demo eligibility limits. It is an **operating mode**, not a license edition. No license document is issued for Demo/Eval mode. The value `"community"` must not appear anywhere in relation to this mode.

**Hard limits for Demo/Eval mode:**

| Resource | Limit |
|---|---|
| Total bookings stored | 5 |
| Staff members | 2 |
| Services | 3 |
| Days since first startup | 30 |

**Behavior:**

- A persistent demo banner is visible in **all** UI views while in Demo/Eval mode.
- When any limit is reached: new bookings and new configurations of the limited resource are blocked. Existing data remains fully readable and exportable.
- The admin dashboard shows a clear, actionable prompt to acquire a commercial license.
- Demo/Eval mode is explicitly tracked via a `first_startup_at` timestamp stored in the application's persistent storage.

> **Note:** Demo/Eval mode is entirely separate from RevenueCat. It is not tied to any RevenueCat product, entitlement, or subscription state. The License Broker does not issue any document for Demo/Eval instances.

---

## 6. RevenueCat Billing Integration

### Architecture — Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────┐
│  PAYMENT AND ENTITLEMENT LAYER (external, cloud-hosted)         │
│                                                                   │
│  [Customer]                                                       │
│      │ pays via Stripe / App Store / Play Store / etc.           │
│      ▼                                                            │
│  [RevenueCat]                                                     │
│      │ manages subscriptions, entitlements, renewals,            │
│      │ cancellations, refunds, trial periods                      │
│      │ Webhooks: INITIAL_PURCHASE / RENEWAL /                    │
│      │           CANCELLATION / REFUND / UNCANCELLATION          │
│      ▼                                                            │
│  [Servario License Broker] ◄── PRIVATE SYSTEM                   │
│      │ (not in public repository; not open source)               │
│      │ Receives RevenueCat webhook                               │
│      │ Verifies entitlement via RevenueCat REST API              │
│      │ Generates Ed25519-signed Servario license document        │
│      │ Delivers license to customer (email / self-service portal)│
│      ▼                                                            │
│  [Customer receives signed license document]                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼ (one-time delivery + online validation)
┌─────────────────────────────────────────────────────────────────┐
│  SELF-HOSTED SERVARIO INSTANCE (customer's infrastructure)       │
│                                                                   │
│  Validates license locally via compiled-in Ed25519 public key    │
│  No direct RevenueCat contact                                     │
│  No RevenueCat secret keys or API credentials                     │
│  Optional background validation against License Broker only      │
└─────────────────────────────────────────────────────────────────┘
```

This architecture ensures that a Servario instance never holds credentials for any third-party billing system, and that RevenueCat credentials are never exposed in the open-source codebase.

---

### RevenueCat Entitlement Mapping

| RevenueCat Entitlement ID | Servario Edition | License issuance |
|---|---|---|
| `servario_starter` | `starter` | Issued by License Broker on entitlement activation |
| `servario_professional` | `professional` | Issued by License Broker on entitlement activation |
| `servario_business` | `business` | Issued by License Broker on entitlement activation |
| (no entitlement) | (none) | Demo/Eval operating mode — no license document |

> **Critical:** `"community"` is NOT a valid entitlement identifier or edition value. This term must not appear in any code, configuration, documentation, or RevenueCat product setup. Any occurrence is an error.

---

### Security Rules for RevenueCat Credentials

| Credential | Location | Access |
|---|---|---|
| RevenueCat Secret API Key | License Broker only | License Broker operator only |
| RevenueCat Webhook Signing Secret | License Broker only | License Broker operator only |
| RevenueCat Public SDK Key (if used) | License Broker / customer-facing portal only | License Broker operator only |
| RevenueCat credentials of any kind | **Never in Servario repository** | **Not accessible to self-hosted instances** |

The self-hosted Servario instance has zero knowledge of, and zero dependency on, RevenueCat. This is a hard architectural constraint.

---

### License Broker Interface

The License Broker is a private service operated by the Servario licensor. Its source code is not published.

**Online validation endpoint:**

```
POST /api/v1/license/validate
Authorization: none (license_id is the opaque identifier)
Content-Type: application/json

Request body:
{
  "license_id":   "UUID",
  "instance_id":  "UUID",
  "version":      "1.2.3",
  "domain":       "booking.example.com"   // optional
}

Response (200 OK):
{
  "status":       "active | grace | revoked | expired",
  "grace_until":  "2026-06-27T08:00:00Z",
  "message":      "human-readable status message"
}
```

**Transport and reliability requirements:**

- HTTPS only; plain HTTP is not accepted.
- 10-second connection and read timeout.
- 1 retry on network-level error (not on 4xx/5xx responses).
- On timeout or unreachable: set `server_unreachable`; apply grace logic.
- The Servario instance must handle License Broker downtime gracefully; downtime must not interrupt customer bookings within the grace window.

---

## 7. Privacy Assessment

### What IS Transmitted During Online Validation

| Field | Description | Privacy classification |
|---|---|---|
| `license_id` | UUID issued by License Broker; opaque, non-personal | Not personal data |
| `instance_id` | Locally generated UUID; no hardware derivation | Generally not personal data [see below] |
| `version` | Servario version string (e.g., `"1.2.3"`) | Not personal data |
| `domain` | Optional; operator-configured hostname | May be pseudonymous personal data [see below] |

### What is NOT Transmitted

- Customer names, email addresses, or any booking participant data.
- Staff member data.
- Business name or address.
- Hardware fingerprints (MAC address, CPU ID, disk serial, etc.).
- Session tokens, authentication headers, or behavioral telemetry.
- Any data from bookings, services, or calendar events.

### GDPR Considerations

**`instance_id`:** Generated as a random UUID at first startup with no hardware binding. It is stored in the application's persistent data directory and persists across restarts. Because it is not derived from hardware or linked to a natural person without additional data held by the licensor, it is generally not personal data under GDPR. However, if the licensor's License Broker links `instance_id` to customer account data (which it may for support purposes), the licensor's privacy notice must describe this processing.

**`domain` (optional field):** If the domain name identifies a natural person (e.g., `firstname-lastname.example.com`), it may constitute pseudonymous personal data under GDPR Article 4(1). This field is optional and must be explicitly configured by the operator. It must never be sent by default. The licensor's privacy notice must cover its processing.

**IP address:** Like any HTTPS server, the License Broker's infrastructure will log the IP address of incoming validation requests. This is standard and expected. The licensor's privacy notice must cover IP address processing as part of routine server operations.

**Data minimization principle (applied):**
- The `domain` field is optional and must default to not being sent.
- No booking, customer, staff, or behavioral data is included in any validation request.
- No authentication headers that could be logged and associated with user sessions.

> [ASSUMPTION] The licensor must publish a privacy notice covering License Broker data processing before any commercial licenses are issued. This is a legal requirement, not an optional step.

---

## 8. Risks and Limits of Technical License Enforcement

Since Servario's source code is publicly visible, a technically proficient operator can, in principle, locate and disable license validation checks. This section honestly assesses what technical measures are worth implementing and what are not.

### Worth Implementing

**Ed25519 signature verification:**
A valid license document cannot be forged without the private key. Even with full source access, an operator cannot generate a license document that passes verification. This meaningfully raises the bar for circumvention: a bypass requires modifying the application code itself (not just generating a fake license file).

**License checks in the API layer (not only at startup):**
Placing enforcement checks at the API endpoints that create bookings (rather than solely at startup) means that bypassing startup checks does not automatically grant unlimited production use. Checks at multiple layers increase the work required for circumvention.

**`allowed_features` and limit fields are signature-protected:**
Since these fields are part of the signed payload, an operator cannot modify them without invalidating the signature. Feature differentiation between editions is therefore cryptographically enforced.

### Not Worth Implementing

**Python source obfuscation:**
Python bytecode obfuscation tools (e.g., PyArmor, Cython compilation) can be trivially reversed by a motivated operator with standard tooling. The maintenance burden is high; the protection is minimal. Contradicts the source-available transparency premise.

**Hardware fingerprinting:**
Binding licenses to hardware identifiers (MAC address, CPU ID, disk serial number) is brittle in containerized deployments (Docker, Kubernetes), breaks on legitimate hardware migrations, and is perceived as hostile by operators. The added friction for legitimate customers outweighs the marginal reduction in circumvention risk.

**Binary-only distribution:**
Distributing only compiled binaries without source directly contradicts the source-available model. It would destroy developer trust and the transparency benefits that source visibility provides.

**Aggressive online validation (frequent pinging, phone-home telemetry):**
Validation more frequent than once per 24 hours, or collection of operational data beyond the minimal validation payload, is privacy-hostile and generates operator distrust. The 24-hour interval with a 30-day grace window is the appropriate balance.

### Primary Defense: Fair Pricing Over Technical Barriers

The primary protection against license circumvention is economic rationality, not technical barriers. An operator who must invest significant engineering time to bypass license checks when a fairly-priced license removes all friction will typically choose the license. Key principles:

- **Accessible pricing:** Starter edition pricing must be reachable for small businesses and individual service providers.
- **Security updates as soft binding:** Security patches and official Docker image updates are provided only for instances with active licenses. This creates legitimate operational incentive to maintain a valid license without blocking access to existing data.
- **Legal protections:** BUSL-1.1 terms are legally enforceable. Production use without a commercial license is a breach of the license terms. The "Servario" trademark should be established to protect against forks that circumvent licensing while using the brand name.
- **Terms of Service:** The Terms of Service must explicitly prohibit circumvention of license checks.

---

## 9. MVP Requirements — License System

The following requirements must be satisfied before the first public production release of Servario. All items are non-negotiable for launch.

| # | Requirement | Details |
|---|---|---|
| L-1 | License file parsing | Read from `SERVARIO_LICENSE_KEY` env var (base64-encoded signed JSON) or from `/data/license.json`. One or the other; env var takes precedence. |
| L-2 | Ed25519 signature verification | Verified at backend startup against the Ed25519 public key compiled into the backend. Uses `PyNaCl` or `cryptography` library. No custom crypto. |
| L-3 | Local-only validation at startup | Signature check requires no network access. Instance can validate its license entirely offline at startup. |
| L-4 | License status in Admin UI | Status badge displaying one of: `active` / `grace` / `expired` / `missing` / `invalid` / `revoked`. Badge color-coded; clicking badge shows detail panel. |
| L-5 | Demo mode enforcement | Hard limits enforced: 5 total bookings, 2 staff members, 3 services, 30 calendar days from first startup. Demo banner visible in all UI views. |
| L-6 | Booking block on expired / invalid / revoked | The create-booking API endpoint returns HTTP 402 (or equivalent business error) when license status is `expired` (grace elapsed), `invalid`, or `revoked`. |
| L-7 | Clear error messages | Admin dashboard shows a specific, actionable message for each license status. Message includes a link to the licensing/purchase page. |
| L-8 | Environment variable support | `SERVARIO_LICENSE_KEY`, `SERVARIO_INSTANCE_ID`, `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` are read at startup. See Appendix for details. |
| L-9 | `SERVARIO_INSTANCE_ID` auto-generation | If `SERVARIO_INSTANCE_ID` is not set, a UUID is generated on first start and persisted to `/data/instance_id`. Subsequent starts read this file. |
| L-10 | No RevenueCat dependency in application | The Servario application code contains zero RevenueCat imports, API calls, or credentials. Verified by code review before any release. |
| L-11 | Invalid license: no Demo/Eval fallback | When a license document is present but invalid (bad signature, malformed), the instance does not fall back to Demo/Eval mode. Status is `invalid` and bookings are blocked. |
| L-12 | LICENSE file at repository root | The repository root must contain a `LICENSE` file with the BUSL-1.1 text, fully populated with Licensor, Licensed Work, Additional Use Grant, Change Date, and Change License. |

---

## 10. Post-MVP Extensions

The following features are planned for implementation after the initial production release, in approximate priority order.

| Feature | Description |
|---|---|
| Online validation against License Broker | Background task runs every 24 hours; calls License Broker validation endpoint; updates `last_validated_at`, `grace_until`, and status. Implements grace/revocation handling per the validation flow. |
| Admin UI: license entry form | Operator can paste a new license key via the admin dashboard without restarting the application. New license is validated in-memory; persisted to `/data/license.json` on confirmation. |
| Admin UI: license detail view | Panel showing: edition, `license_id` (truncated), `expires_at`, `max_staff`, `max_services`, `allowed_features`, `last_validated_at`, `grace_until`. Provides operator visibility without exposing full signed document. |
| Automatic renewal reminders | Email or in-app notifications at 30, 7, and 1 day before `expires_at`. Requires admin email configuration. |
| Edition-based feature flags | Backend reads `allowed_features` array from license document; feature gates check array membership at API and UI layers. |
| Starter / Professional / Business differentiation | Define and document the specific limits and features for each edition. Implement `max_staff`, `max_services`, `max_bookings_per_month` enforcement against license document values. |
| Key rotation support | Compile multiple valid public keys into the backend to support smooth rotation during key transitions. Validation succeeds if any known public key verifies the signature. |
| Audit log for license events | Persistent log of: license loaded, validation succeeded/failed, status changed, Demo limit reached. Accessible from Admin UI. |
| License Broker self-service portal | Customer-facing web portal where license holders can view, download, and regenerate their license documents, manage instance IDs, and update contact information. (License Broker scope, not Servario application scope.) |

---

## Appendix: Environment Variable Reference

| Variable | Default | Required | Description |
|---|---|---|---|
| `SERVARIO_LICENSE_KEY` | (empty) | No | Base64-encoded signed license JSON document. If set, takes precedence over `/data/license.json`. If neither is set, instance starts in Demo/Eval mode (if within demo limits). |
| `SERVARIO_LICENSE_SERVER_URL` | (empty) | No | Base URL of the License Broker validation endpoint (e.g., `https://license.servario.io`). If empty, online validation is disabled and the instance operates in offline mode (subject to grace period logic). |
| `SERVARIO_INSTANCE_ID` | (auto-generated) | No | UUID identifying this installation. If not set, auto-generated on first start and persisted to `/data/instance_id`. Should remain stable across restarts and upgrades. Sent to License Broker during online validation only. |
| `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` | `30` | No | Number of days of offline operation permitted after the last successful online validation before bookings are blocked. Range: 1–90. Applies only when `SERVARIO_LICENSE_SERVER_URL` is configured and the License Broker is unreachable. |

---

*This document is the authoritative reference for Servario's license model, technical enforcement architecture, and billing integration design. It supersedes any prior informal discussions, README statements, or code comments regarding the license. All items marked [ASSUMPTION] require a decision by the project owner before the first public release.*
