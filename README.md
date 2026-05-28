<p align="center">
  <img src="./assets/servario-cover.png" alt="Servario Open Service Scheduling" width="100%">
</p>

<h1 align="center">Servario</h1>

<p align="center">
  <strong>Open Service Scheduling for self-hosted, privacy-conscious service operations.</strong>
</p>

<p align="center">
  Servario is an open-source scheduling system for managing services, calendars, team availability, customer bookings, roles, APIs, automations and integrations in one modular architecture.
</p>

<p align="center">
  <a href="#project-status">Project Status</a>
  ·
  <a href="#core-modules">Core Modules</a>
  ·
  <a href="#architecture">Architecture</a>
  ·
  <a href="#roadmap">Roadmap</a>
  ·
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/badge/license-AGPL--3.0-6E7FF3?style=flat-square">
  <img alt="Status" src="https://img.shields.io/badge/status-early%20planning-8A8F98?style=flat-square">
  <img alt="Self Hosted" src="https://img.shields.io/badge/self--hosted-first-2BBBAD?style=flat-square">
  <img alt="Open Source" src="https://img.shields.io/badge/open--source-auditable-9B6DFF?style=flat-square">
</p>

---

## Purpose

Servario is designed for organizations that need transparent, maintainable and self-hosted service scheduling without depending on closed booking platforms.

The project focuses on:

- calendar-based service scheduling
- team and resource availability
- customer-facing booking pages
- role-based access control
- API-driven integrations
- notifications and automation workflows
- self-hosted infrastructure ownership
- privacy-conscious deployment models

Servario is not intended to be a decorative SaaS clone. It is built around clear system boundaries, predictable behavior and technical credibility.

---

## Project Status

> Servario is currently in the early project definition phase.

The repository is being prepared as an open-source project. Core concepts, visual direction, terminology, motion principles and architecture boundaries are being defined before implementation begins.

| Area | Status |
|---|---|
| Project identity | Defined |
| Repository structure | In preparation |
| Visual cover direction | Defined |
| Motion principles | Defined |
| Core modules | Drafted |
| Technical stack | Not finalized |
| First implementation | Pending |

---

## Core Modules

Servario is structured as a modular scheduling system. Each module has a defined responsibility and should remain independently understandable.

| Module | Responsibility |
|---|---|
| Calendar | Time slots, availability, occupied periods and scheduling visibility |
| Services | Service catalog, durations, constraints and booking rules |
| Team Members | Staff availability, assignment and role-related scheduling behavior |
| Customers | Customer records, booking context and communication references |
| Booking Page | Public-facing entry point for service selection and appointment requests |
| Scheduling Engine | Availability checks, conflict handling and slot assignment |
| API | Stable integration boundary for external systems and clients |
| Integrations | Calendar sync, webhooks, external tools and automation bridges |
| Notifications | Email, SMS, in-app or webhook-based booking updates |
| Automations | Rule-based workflows triggered by booking and scheduling events |
| Access & Roles | Permission model for administrative and operational access |
| Self-Hosted Infrastructure | Deployment, persistence, networking, monitoring and backups |

---

## Architecture

Servario follows a clear modular architecture. The calendar is important, but it is not the entire system. Scheduling emerges from the interaction between services, team members, customers, booking rules, roles and infrastructure.

```text
Services        Team Members        Customers
   │                 │                  │
   └──────┬──────────┴──────┬───────────┘
          │                 │
          ▼                 ▼
      Calendar        Booking Page
          ▲                 │
          │                 ▼
          └────── Scheduling Engine
                         │
                         ▼
                        API
                         │
                         ▼
                   Integrations

Calendar ─────────► Notifications
Calendar ─────────► Automations

Access & Roles ───► Calendar
Access & Roles ───► Services
Access & Roles ───► Team Members
Access & Roles ───► Customers
Access & Roles ───► API
Access & Roles ───► Automations

Self-Hosted Infrastructure supports all modules.
