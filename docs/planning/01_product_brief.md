# Servario — Product Brief

**Document status:** Draft
**Last updated:** 2026-05-28
**Audience:** Product, engineering, and commercial stakeholders

---

## 1. Product Vision

Servario is a self-hosted, source-available scheduling and booking platform built for service businesses. It is designed for owners who want full control over their customer data, their infrastructure, and their user experience — without depending on a SaaS provider or sending sensitive appointment data to third-party servers.

The core promise: install Servario on your own server, point your customers at the public booking page, and receive appointments. Everything runs on infrastructure you own.

**Primary use cases:**

- A hair salon owner running Servario on a VPS, taking bookings 24/7 without a monthly SaaS fee
- A private tutor offering a clean booking page that matches their personal brand
- A consultant managing availability and client meetings from a self-hosted admin dashboard
- A developer deploying Servario for a client who wants to own their booking data

Servario is not a hosted service. There is no Servario cloud. The software ships as a Docker Compose stack — bring your own server.

---

## 2. Target Audience

### Primary: Small service businesses

Solo operators and small teams (1–10 staff) providing appointment-based services: hair and beauty, tutoring, consulting, therapy, fitness, photography, legal, and similar fields. These businesses need:

- A public-facing booking page that works on mobile
- Staff availability management with scheduling rules
- Email confirmations and reminders for both staff and customers
- A simple admin dashboard to manage the calendar

### Secondary: Self-hosters

Privacy-conscious individuals and technically capable small business owners who prefer running software on their own hardware or VPS. They value:

- Full ownership of customer data (GDPR compliance on their terms)
- No vendor lock-in or account termination risk
- Ability to inspect the source code before deploying it

### Tertiary: Developers deploying for clients

Freelance developers and agencies who want to offer a white-label-ready (future) or lightly customized booking system to their clients. In MVP, developers can deploy and configure Servario for clients; white-labeling is a post-MVP goal.

---

## 3. Core Features (MVP)

### 3.1 Service Catalog

- Define services with: name, description, duration (minutes), price (display only — no online payment in MVP), buffer time before/after
- Enable or disable services independently
- [ASSUMPTION] Maximum of 50 services per instance in Starter edition; higher limits in Professional and Business

### 3.2 Staff Management

- Create staff profiles with name, contact email, and optional bio/photo
- Define weekly availability templates (recurring schedule)
- Add availability exceptions: blocked days, one-off open hours, holidays
- Assign staff to one or more services
- [ASSUMPTION] Staff calendars are independent — no cross-staff conflict detection in MVP

### 3.3 Public Booking Page

- Accessible without customer login or registration
- Service → staff (or auto-assign) → date/time → customer details → confirmation
- Mobile-responsive, minimal design
- No captcha required in MVP [ASSUMPTION: spam mitigation deferred to post-MVP]
- Booking confirmation page with summary; confirmation email sent automatically

### 3.4 Admin Dashboard

- Calendar view: day, week, and month perspectives
- Booking management: view, confirm, reschedule, cancel bookings
- Settings panel: business name, timezone, email configuration, license status
- Staff and service CRUD
- Customer list with search and soft-delete (GDPR)

### 3.5 Email Notifications

- Booking confirmation (to customer and staff)
- Appointment reminder (configurable lead time, e.g. 24 hours before)
- Cancellation notice (to customer and staff)
- [ASSUMPTION] SMTP configuration required; no bundled mail service in MVP

### 3.6 Customer Record Management

- Customer records created automatically at booking time (name, email, phone)
- Admin can view, edit, and soft-delete customer records
- Soft delete anonymizes personal data in place; booking history is preserved in anonymized form
- Hard delete available for explicit GDPR erasure requests
- [ASSUMPTION] No customer self-service account or login in MVP

### 3.7 License Management

- License status displayed prominently in the admin dashboard
- Demo/Eval mode enforces hard limits (see Section 4)
- Admin is notified when demo limits are approaching or reached
- License key entry and validation UI in settings panel
- Grace period handling: if online validation is unavailable, a configurable offline grace period applies before enforcement tightens

---

## 4. License and Commercial Model

This section is critical. It defines the legal and commercial basis for Servario and must be reflected accurately in all documentation, README files, and marketing materials.

### 4.1 Servario is Source-Available, Not Open Source

Servario's source code is publicly available for inspection, audit, and contribution. However, source availability does **not** grant a license for free production use.

**Production use of Servario requires a valid, paid license.**

The license is **BUSL-1.1** (Business Source License 1.1). Under BUSL-1.1:

- The source code is publicly readable and auditable
- Production use requires a commercial license (purchased via the Servario licensing system)
- After four years from each file's release date, the code converts to Apache 2.0 for that version
- No CLA is required for the license grant itself, but contributors must sign a Contributor License Agreement (CLA) to have their patches merged

### 4.2 Why Source-Available?

**Auditability and security transparency:** Service businesses handle customer contact data and appointment schedules. Self-hosters need to be able to inspect the code running on their servers. Source availability enables security audits, vulnerability disclosure, and community trust — without granting free production use.

**Community trust:** A closed binary would prevent self-hosters from verifying what the software does. Source availability is a commitment to transparency.

**Why not fully open source (e.g., MIT or Apache 2.0):** Fully permissive licenses allow any party to take the software, run it commercially, or compete directly with the project without contributing back. Servario is a commercially developed product; sustainable development requires revenue.

**Why not AGPL-3.0:** AGPL-3.0 is an OSI-approved open source license. Under AGPL Section 10, no additional restrictions may be placed on the freedoms granted by the license — including the freedom to use the software in production for free. **AGPL-3.0 would directly contradict the requirement that production use requires a paid license.** AGPL-3.0 is not the license for Servario. It must not appear in any license badge, README section, code comment, or planning document as the Servario license.

### 4.3 Demo and Evaluation Mode

Servario can be run without a license for evaluation purposes. Demo/Eval mode is subject to the following **hard limits**, enforced in code:

| Limit | Value |
|---|---|
| Maximum total bookings | 5 |
| Maximum staff accounts | 2 |
| Maximum services | 3 |
| Maximum operating window | 30 days from first startup |

These limits are not soft warnings — they are enforced. Once a limit is reached, the affected action is blocked. The admin sees a clear message indicating which limit was reached and how to obtain a license.

**Demo/Eval mode is for evaluation only.** It is not a "free tier" or a "community edition." There is no perpetual free use option.

### 4.4 License Editions

Three editions are available. The specific feature differentiation between editions is to be finalized, but the edition names and tier structure are fixed:

| Edition | Intended for |
|---|---|
| **Starter** | Solo operators, very small teams |
| **Professional** | Small businesses with multiple staff |
| **Business** | Larger teams, advanced configuration needs |

**There is no "Community" edition.** A "Community" edition name would imply perpetual free production use, which contradicts the commercial model. The evaluation period fills the role that community editions typically serve in other projects, but with explicit time and usage limits.

### 4.5 License Status and Enforcement

| License status | Behavior |
|---|---|
| `valid` | Full access per edition limits |
| `missing` | Demo/Eval mode permitted until limits are reached |
| `invalid` | **No fallback to Demo/Eval mode.** Admin access and data export remain available. New bookings are blocked. |
| `expired` | Same as `invalid` — no Demo/Eval fallback |

The distinction between `missing` and `invalid` is intentional and security-relevant. An `invalid` license may indicate tampering, a revoked license, or a replay attack. Falling back to Demo mode in this case would undermine the enforcement model.

### 4.6 Billing Architecture

Payments and subscriptions are managed through **RevenueCat**. The billing architecture is:

```
Customer payment → RevenueCat → License Broker (private) → Ed25519-signed license document → Servario instance
```

Key properties:

- **RevenueCat secret keys, webhook secrets, and API keys must never be present in the self-hosted Servario instance.** These keys exist only in the License Broker, which is a private, separately deployed service.
- The Servario instance validates its license by verifying the Ed25519 signature on the license document. It does not call RevenueCat directly.
- The License Broker translates RevenueCat entitlement events into signed license documents.

RevenueCat entitlement mapping:

| RevenueCat entitlement | Servario edition |
|---|---|
| `servario_starter` | Starter |
| `servario_professional` | Professional |
| `servario_business` | Business |

Demo/Eval mode is not a RevenueCat product or entitlement. It is a license-less operating mode built into Servario itself.

---

## 5. MVP Scope Boundary

### Included in MVP

- Service catalog management
- Staff profiles and availability rules
- Public booking page (no customer login)
- Admin dashboard (calendar, booking management, settings)
- Email notifications (confirmation, reminder, cancellation) via SMTP
- Customer records with GDPR soft-delete and hard-delete
- License management UI (status, demo limits, license key entry)
- Docker Compose deployment with Nginx Proxy Manager support
- PostgreSQL database backend
- Python/FastAPI backend
- Next.js frontend

### Explicitly Deferred (Post-MVP)

- **Online payments:** No Stripe, PayPal, or other payment processing in the booking flow. Price is displayed for information only.
- **Multi-tenant / multi-organization:** MVP is single-organization. One Servario instance serves one business. No `org_id` separation in domain tables.
- **Mobile application:** No native iOS or Android app. The public booking page and admin dashboard are mobile-responsive web UIs.
- **Customer accounts:** Customers do not log in or create accounts in MVP. Bookings are created anonymously (with contact info).
- **White-labeling:** No theme customization or logo replacement beyond basic business name/branding in MVP.
- **Plugin or extension marketplace:** No plugin API or third-party extension system in MVP.
- **Two-way calendar sync:** No Google Calendar, Outlook, or CalDAV sync in MVP.
- **SMS notifications:** Email only in MVP.
- **Webhook outbound events:** No external webhook system in MVP.

---

## 6. Non-Goals

The following are explicitly out of scope for Servario, now and in the foreseeable future unless the project direction changes with documented rationale:

- **No SaaS offering:** Servario is self-hosted only. The project principals will not operate a hosted version of Servario. The value proposition is self-hosting.
- **No multi-tenancy in MVP:** A single Servario instance serves a single organization. There is no shared infrastructure or tenant isolation model.
- **No open-source relicensing:** Servario will not be relicensed to MIT, Apache 2.0, GPL, or AGPL. The source-available, BUSL-1.1 model is the commercial foundation of the project.
- **No "Community" edition:** See Section 4.4. There is no perpetually free production tier.
- **No plugin marketplace in MVP:** Third-party extensibility is a post-MVP concern. The MVP ships a focused, well-tested core.
- **No white-labeling in MVP:** Customization is limited to business name and basic settings. Full white-labeling (custom domain for booking page, custom email templates, logo replacement) is post-MVP.
