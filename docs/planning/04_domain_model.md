# 04 — Domain Model

> Status: Planning / Pre-Implementation
> Audience: Backend Architect, QA Architect, Security Reviewer
> Language: English

---

## Design Principles

- **Single-org model**: no `organization_id` in any domain table; one Servario instance serves one business
- **GDPR-compliant soft-delete** for customers: personal fields nulled, booking records retained
- **Append-only audit log**: no modification or deletion of audit entries
- **Booking conflict prevention**: PostgreSQL `tstzrange` exclusion constraint (not a partial unique index)
- **No multi-tenancy** in MVP: multi-org use cases are served by running separate instances

---

## Entity Overview

| Entity | Description |
|---|---|
| Settings | Single-row configuration for the Servario instance |
| User | Admin/staff users who can log in to the admin dashboard |
| TeamMember | A staff member who provides services; may or may not have a User login |
| AvailabilityRule | Recurring weekly availability schedule for a TeamMember |
| AvailabilityException | One-off override (blocked day or special hours) for a TeamMember |
| Service | A bookable service with name, duration, and price |
| ServiceTeamMember | N:M junction: which TeamMembers offer which Services |
| Customer | A person who makes bookings; GDPR-soft-deletable |
| Booking | A confirmed or pending appointment between Customer, TeamMember, and Service |
| Notification | Delivery log for emails sent about a Booking |
| AuditLog | Append-only record of all significant actions in the system |

---

## Entity Definitions

### Settings

Single row per instance (`id` is always `1`). Stores business identity and SMTP configuration.

| Field | Type | Notes |
|---|---|---|
| id | INTEGER | Always 1 |
| business_name | VARCHAR | Displayed on public booking page |
| business_email | VARCHAR | Contact email |
| business_phone | VARCHAR | Optional |
| business_address | TEXT | Optional |
| booking_page_title | VARCHAR | Title shown on public booking page |
| booking_page_description | TEXT | Subtitle/description on public booking page |
| timezone | VARCHAR | Default `UTC`; IANA timezone identifier |
| smtp_host | VARCHAR | SMTP server hostname |
| smtp_port | INTEGER | Default 587 |
| smtp_user | VARCHAR | SMTP username |
| smtp_password_encrypted | VARCHAR | Encrypted at rest |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### User

Admin and staff users who authenticate to the admin dashboard.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| email | VARCHAR | UNIQUE NOT NULL |
| password_hash | VARCHAR | bcrypt NOT NULL |
| display_name | VARCHAR | |
| role | ENUM | `owner` \| `staff` \| `admin` |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

**Roles:**
- `owner`: full access including settings and billing
- `admin`: same as owner minus billing/license management
- `staff`: own calendar and limited booking access

---

### TeamMember

A person who delivers services. May be linked to a User (for login) or exist as a staff record only.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID FK | → User; nullable (TeamMember may have no login) |
| display_name | VARCHAR | NOT NULL; shown on public booking page |
| email | VARCHAR | Optional; used for notifications |
| bio | TEXT | Optional; shown on public booking page |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### AvailabilityRule

Recurring weekly availability for a TeamMember.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| team_member_id | UUID FK | → TeamMember NOT NULL |
| day_of_week | SMALLINT | 0 = Monday … 6 = Sunday |
| start_time | TIME | |
| end_time | TIME | Must be after start_time |
| is_active | BOOLEAN | Default true |

---

### AvailabilityException

One-off override for a specific date: blocked day or special hours.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| team_member_id | UUID FK | → TeamMember NOT NULL |
| exception_date | DATE | NOT NULL |
| is_blocked | BOOLEAN | If true, no bookings on this date |
| start_time | TIME | Nullable; used when `is_blocked = false` |
| end_time | TIME | Nullable; used when `is_blocked = false` |
| note | TEXT | Optional; internal use |

---

### Service

A bookable service offered by the business.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | VARCHAR | NOT NULL |
| description | TEXT | Shown on public booking page |
| duration_minutes | INTEGER | NOT NULL; must be > 0 |
| price | NUMERIC(10,2) | Optional; null = price on inquiry |
| currency | VARCHAR(3) | ISO 4217; e.g. `EUR` |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### ServiceTeamMember

N:M junction table: which TeamMembers offer which Services.

| Field | Type | Notes |
|---|---|---|
| service_id | UUID FK | → Service NOT NULL |
| team_member_id | UUID FK | → TeamMember NOT NULL |
| PRIMARY KEY | | (service_id, team_member_id) |

---

### Customer

A person who makes bookings. GDPR soft-delete: personal fields nulled when erasure requested.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | VARCHAR | Nulled on GDPR delete |
| email | VARCHAR | Nulled on GDPR delete |
| phone | VARCHAR | Nulled on GDPR delete |
| notes | TEXT | Nulled on GDPR delete |
| gdpr_deleted_at | TIMESTAMPTZ | Set when erasure request fulfilled |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

**GDPR soft-delete behavior**: when `gdpr_deleted_at` is set, all personal fields are nulled. The Customer record itself is retained so that Booking history (service, staff, timestamps) remains intact for business records. An AuditLog entry records the deletion event.

---

### Booking

A scheduled appointment. The `tstzrange` exclusion constraint prevents overlapping bookings for the same TeamMember.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| service_id | UUID FK | → Service NOT NULL |
| team_member_id | UUID FK | → TeamMember NOT NULL |
| customer_id | UUID FK | → Customer NOT NULL |
| start_at | TIMESTAMPTZ | NOT NULL |
| end_at | TIMESTAMPTZ | NOT NULL; must be after start_at |
| status | ENUM | `pending` \| `confirmed` \| `cancelled` \| `no_show` \| `completed` |
| customer_notes | TEXT | Notes from the customer at booking time |
| internal_notes | TEXT | Admin/staff notes; not visible to customer |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### Notification

Delivery log for emails sent about a Booking.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| booking_id | UUID FK | → Booking NOT NULL |
| notification_type | ENUM | `confirmation` \| `reminder` \| `cancellation` \| `reschedule` |
| channel | ENUM | `email` (only channel in MVP) |
| recipient_email | VARCHAR | Snapshot at send time (customer email may later be GDPR-nulled) |
| sent_at | TIMESTAMPTZ | Nullable until sent |
| status | ENUM | `pending` \| `sent` \| `failed` |
| error_message | TEXT | Nullable; populated on failure |

---

### AuditLog

Append-only. No row is ever modified or deleted.

| Field | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| actor_type | ENUM | `user` \| `system` \| `public` |
| actor_id | UUID | Nullable (null for `system` and `public`) |
| action | VARCHAR | e.g. `booking.created`, `customer.gdpr_deleted`, `license.status_changed` |
| entity_type | VARCHAR | e.g. `booking`, `customer`, `settings` |
| entity_id | UUID | Nullable for actions not tied to a single entity |
| changes_json | JSONB | Before/after snapshot for mutations; nullable for creates/deletes |
| created_at | TIMESTAMPTZ | NOT NULL |

**Events to log**: booking created/confirmed/cancelled/completed/no_show, customer GDPR deleted, admin login/logout, settings changed, license status changed, service created/updated/deactivated, staff created/updated/deactivated.

---

## Booking Conflict Prevention

A partial unique index on `(team_member_id, start_at)` is **insufficient** — it only prevents identical start times, not overlapping intervals.

The correct approach is a `tstzrange` exclusion constraint:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE bookings
ADD CONSTRAINT no_overlapping_bookings
EXCLUDE USING gist (
    team_member_id WITH =,
    tstzrange(start_at, end_at, '[)') WITH &&
)
WHERE (status IN ('pending', 'confirmed'));
```

**How it works**: the `[)` interval is half-open (inclusive start, exclusive end). Two bookings overlap if and only if their intervals have a non-empty intersection (`&&`). The `WHERE` clause excludes `cancelled`, `no_show`, and `completed` bookings from the constraint — those do not block new bookings.

**Under concurrent load**: use serializable transaction isolation for booking creation to prevent TOCTOU (time-of-check/time-of-use) race conditions where two requests pass the availability check before either is committed.

---

## Booking Lifecycle

```
(new request)
      │
      ▼
  pending ──────────────────────────► cancelled
      │         (customer cancels,          │
      │          timeout, admin cancels)    │
      │                                     │
      ▼                                     │
  confirmed ───────────────────────► cancelled
      │         (admin/customer cancels)    │
      │                                     │
      ├────────────────────────────► completed
      │         (after appointment time,    │
      │          customer attended)         │
      │                                     │
      └────────────────────────────► no_show
                (after appointment time,
                 customer did not attend)
```

---

## Entity Relationship Summary

```
Settings (1 row per instance)

User ──────────────── TeamMember ─── AvailabilityRule
(optional FK)              │
                           ├────────── AvailabilityException
                           │
                           └────────── ServiceTeamMember ─── Service


Customer ─── Booking ─── Notification
                 │
          tstzrange exclusion constraint
          (no overlap for same TeamMember
           in pending/confirmed status)

AuditLog (references any entity by type + id)
```

---

## License Module Entities

The license module operates outside the booking domain but is a core system component. It does not have database tables in the MVP — the license document is an Ed25519-signed JSON file validated in memory.

| Concept | Storage |
|---|---|
| License document | File or env var (`SERVARIO_LICENSE_KEY`) |
| Instance ID | `/data/instance_id` file (auto-generated UUID) |
| License status | In-memory enum; surfaced via `/api/admin/license/status` endpoint |
| Demo mode counters | Queried from the bookings/staff/services tables at runtime |

---

*All items marked `[ASSUMPTION]` represent design decisions not yet confirmed by the project owner.*
