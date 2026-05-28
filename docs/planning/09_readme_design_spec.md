# Servario — README Design Specification

**Document status:** Draft
**Last updated:** 2026-05-28
**Audience:** Documentation & README Designer (Agent 8); anyone writing or reviewing the project README

This document specifies the design, structure, tone, and exact wording requirements for the Servario `README.md`. It is a binding specification: the README must comply with all requirements in this document, including prohibited language and required badge set.

---

## 1. Overall Tone

The README speaks directly to a technically competent audience: developers setting up a self-hosted service, small business owners who know how to run Docker, and freelancers evaluating the software for client deployments.

**Tone guidelines:**

- **Professional but approachable.** Not academic, not sales-copy. Write as if explaining the project to a competent colleague.
- **No hype.** Avoid superlatives ("best-in-class", "blazing fast", "revolutionary"). Servario is a solid, focused booking tool — describe it as such.
- **Honest about license requirements.** The README must not obscure or downplay the fact that production use requires a license. The licensing model is a feature of the project's transparency, not a liability to be hidden.
- **Self-hosters as the audience.** The Quick Start section assumes the reader has Docker and Docker Compose installed and knows what a `.env` file is. Do not over-explain basics.
- **No SaaS framing.** Do not write "sign up", "subscribe to our cloud", or "managed hosting". Servario is self-hosted. The reader is installing software on their own server.

---

## 2. Badge Design

Badges appear at the top of the README, in the header section, below the project logo placeholder and above the tagline.

### Required badges

The following five badges are required. They must appear in this order. Do not substitute alternative badge colors or label text.

| Badge | Label | Message | Color |
|---|---|---|---|
| License | `license` | `Source Available` | `#6E7FF3` |
| Production use | `production use` | `requires license` | `#E8624A` |
| Status | `status` | `early development` | `#8A8F98` |
| Self-hosted | `self-hosted` | `first` | `#2BBBAD` |
| Source | `source` | `auditable` | `#9B6DFF` |

**Badge markup (shields.io, flat-square style):**

```html
<img alt="License" src="https://img.shields.io/badge/license-Source%20Available-6E7FF3?style=flat-square">
<img alt="Production Use" src="https://img.shields.io/badge/production%20use-requires%20license-E8624A?style=flat-square">
<img alt="Status" src="https://img.shields.io/badge/status-early%20development-8A8F98?style=flat-square">
<img alt="Self Hosted" src="https://img.shields.io/badge/self--hosted-first-2BBBAD?style=flat-square">
<img alt="Source" src="https://img.shields.io/badge/source-auditable-9B6DFF?style=flat-square">
```

### Removed / prohibited badges

The following badges must not appear in the README under any circumstances:

| Prohibited badge | Reason for removal |
|---|---|
| `license-AGPL--3.0` (any variant) | AGPL-3.0 is not the license for Servario. Including this badge is legally and commercially incorrect. |
| `open--source-auditable` or any badge combining "open source" with "auditable" | Incorrect framing. Servario is source-available, not open source. "Open source" has a specific legal meaning (OSI definition) that does not apply to BUSL-1.1 software. |
| Any OSI "Open Source" logo or badge | Servario is not an OSI-approved open source project. |
| `license-MIT`, `license-Apache--2.0`, `license-GPL` | Incorrect licenses. |

---

## 3. README Structure

The README sections must appear in the following order. No sections may be reordered without updating this specification.

| Order | Section | Purpose |
|---|---|---|
| 1 | Header | Logo placeholder, badges, project name |
| 2 | One-line tagline | Single sentence; what Servario is |
| 3 | Short description | 3–5 sentences expanding on the tagline |
| 4 | Features table | MVP features in a two-column table |
| 5 | Quick Start | Docker Compose; three commands to get running |
| 6 | License | Exact wording specified in Section 4 of this document |
| 7 | Contributing | CLA requirement; link to CONTRIBUTING.md |

### 3.1 Header

```markdown
<!-- Logo placeholder: replace with actual logo when available -->
<p align="center">
  <img src="docs/logo-placeholder.png" alt="Servario" width="200">
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-Source%20Available-6E7FF3?style=flat-square">
  <img alt="Production Use" src="https://img.shields.io/badge/production%20use-requires%20license-E8624A?style=flat-square">
  <img alt="Status" src="https://img.shields.io/badge/status-early%20development-8A8F98?style=flat-square">
  <img alt="Self Hosted" src="https://img.shields.io/badge/self--hosted-first-2BBBAD?style=flat-square">
  <img alt="Source" src="https://img.shields.io/badge/source-auditable-9B6DFF?style=flat-square">
</p>

# Servario
```

### 3.2 One-line tagline

The tagline must be a single sentence. It must not contain the words "open source". [ASSUMPTION] Suggested text:

> Self-hosted appointment and booking platform for service businesses.

### 3.3 Short description

3–5 sentences. Must cover: what Servario does, who it is for, that it is self-hosted, and that source is available for audit. Must not claim it is open source. [ASSUMPTION] Suggested text:

> Servario lets you run your own appointment booking system on your own server. It is built for hair salons, tutors, consultants, and other service businesses that want a professional booking page without sending customer data to third-party servers. The source code is publicly available for review and audit. Production use requires a license.

### 3.4 Features table

A two-column Markdown table listing MVP features. Left column: feature name. Right column: brief description.

[ASSUMPTION] Example structure — expand with finalized feature list:

| Feature | Description |
|---|---|
| Service catalog | Define services with name, duration, price, and description |
| Staff management | Availability rules, exceptions, and service assignments |
| Public booking page | No customer login required; mobile-responsive |
| Admin dashboard | Calendar view, booking management, settings |
| Email notifications | Confirmation, reminder, and cancellation emails via SMTP |
| Customer records | GDPR-compliant soft delete and hard delete |
| License management | Demo mode with clear limits; license key entry and status display |
| Docker Compose deployment | Standard self-hosted stack with Nginx Proxy Manager support |

### 3.5 Quick Start

See Section 6 of this document for the detailed Quick Start design.

### 3.6 License section

See Section 4 of this document for the exact required wording.

### 3.7 Contributing section

Must include:

- A statement that contributions are welcome
- A clear statement that a Contributor License Agreement (CLA) is required
- A link to `CONTRIBUTING.md`
- Must not claim the project is open source

[ASSUMPTION] Suggested text:

```markdown
## Contributing

Contributions are welcome. Before your first pull request is merged, you must sign the
Contributor License Agreement (CLA). See [CONTRIBUTING.md](./CONTRIBUTING.md) for the
process and guidelines.

Servario is source-available, not an open-source project. Please read the license section
below before contributing.
```

---

## 4. License Section — Exact Wording

The following text must appear verbatim in the `## License` section of the README. It may not be paraphrased, shortened, or reordered without updating this specification.

```markdown
## License

Servario's source code is publicly available for review, audit, and contribution.

**Production use requires a valid license.** Licenses are available at [project website].

Development, evaluation, and demo use is permitted without a license, subject to the limits
described in the [Demo Mode documentation].

The full license terms are in the [LICENSE](./LICENSE) file. Third-party dependency licenses
are listed in [NOTICE](./NOTICE).
```

**Notes on this wording:**

- "[project website]" is a placeholder. Replace with the actual URL when the website is live.
- "[Demo Mode documentation]" is a placeholder. Replace with a link to the demo mode documentation page or section when it exists.
- The word "production" is intentionally bolded to draw attention to the key constraint.
- The phrase "publicly available" is used deliberately instead of "open source". These are not synonyms.

---

## 5. Prohibited Language

The following phrases and terms must **never** appear in the README. The list is exhaustive for known high-risk terms; good judgement applies to paraphrases.

| Prohibited phrase | Why it is prohibited |
|---|---|
| "open-source project" | Servario is not an OSI-approved open source project |
| "open source scheduling system" | Same as above |
| "open source booking" | Same as above |
| "AGPL-3.0" | Not the license; legally and commercially incorrect |
| "free to use under AGPL" | Incorrect; AGPL is not the license |
| "fork-able under AGPL" | Incorrect; AGPL is not the license |
| "free to use" (without qualification) | All production use requires a license |
| "community edition" | There is no Community edition; this implies free production use |
| "open-source auditable" | Conflates source-available with open source |
| "sign up" or "our cloud" | Servario has no SaaS offering |
| "free for self-hosters" | Incorrect; self-hosting in production requires a license |

---

## 6. Quick Start Section Design

The Quick Start section must be operable by a developer in under five minutes on a machine with Docker and Docker Compose installed. It consists of exactly three commands, a note about the `.env` file, and a note about production licensing.

### Design

````markdown
## Quick Start

> **Requirements:** Docker and Docker Compose. Tested on Linux and macOS.

```bash
# 1. Clone the repository
git clone https://github.com/[org]/servario.git
cd servario

# 2. Copy and edit the environment file
cp .env.example .env
# Open .env in your editor and set at minimum: POSTGRES_PASSWORD, SMTP settings

# 3. Start the stack
docker compose up -d
```

Servario will be available at `http://localhost:3000` by default.
The admin dashboard is at `http://localhost:3000/admin`.

**Production use requires a license key.** Set `SERVARIO_LICENSE_KEY` in your `.env` file.
Without a license key, Servario runs in Demo/Eval mode (5 bookings, 2 staff, 3 services, 30 days).

For full deployment instructions including Nginx Proxy Manager setup and HTTPS configuration,
see the [deployment documentation](./docs/deployment.md). [ASSUMPTION: path TBD]
````

### Requirements for the Quick Start section

- Exactly three numbered commands (clone, copy env, up)
- The `docker compose` command uses the modern syntax (no hyphen), not `docker-compose`
- A note about Demo/Eval mode limits must appear in the Quick Start section — users must know the limits before they deploy
- A note about production license requirement must appear
- No RevenueCat configuration instructions appear here; license key configuration is all that is needed by the self-hoster
- [ASSUMPTION] Port 3000 is the default frontend port; confirm with DevOps Architect before finalizing

---

## 7. Revision Notes

This specification will be updated when:

- The project website URL is finalized (replace `[project website]` placeholders)
- The demo mode documentation is written (replace `[Demo Mode documentation]` placeholder)
- The deployment documentation path is confirmed (replace `./docs/deployment.md` placeholder)
- The logo is finalized (replace logo placeholder in Section 3.1)
- The default port is confirmed (replace port 3000 assumption in Section 6)
- Any new badge is proposed (must be reviewed against Section 2 requirements)

All placeholder values are marked with `[ASSUMPTION]` or bracketed text. Before the README is published, all placeholders must be resolved or explicitly deferred with a note.
