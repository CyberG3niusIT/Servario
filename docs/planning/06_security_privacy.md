# 06 — Security & Privacy

## 1. Threat Model Overview

### Actors

| Actor | Description | Trust Level |
|---|---|---|
| **Admin users** | Operators who manage services, staff, bookings, and settings via the admin UI | High (authenticated) |
| **Staff** | Employees or contractors who may have limited admin access | Medium (authenticated, scoped) |
| **Customers / Public** | Anyone accessing the public booking page; no login required | Untrusted |
| **Hosting operator** | The individual or organisation that runs the self-hosted instance | Full infrastructure access (trusted by design) |
| **Software vendor / licensor** | Servario as a company; issues signed licenses and receives license validation pings | External trusted service |

### Assets

| Asset | Sensitivity | Where Stored |
|---|---|---|
| Booking data | Medium — appointment times, service details | PostgreSQL |
| Customer PII (name, email, phone, notes) | High — GDPR-relevant | PostgreSQL |
| Admin credentials (email + password hash) | High | PostgreSQL |
| License key | Medium — business-critical | Env var / `/data/license.json` |
| SMTP credentials | High — enables email impersonation | Database (encrypted) |
| Session signing key (`SECRET_KEY`) | Critical — session forgery risk | Env var only |
| Database URL | High — full data access | Env var only |

### Primary Threats

- **Credential theft**: admin password brute-forced or leaked via insecure storage.
- **Session hijacking**: session cookie intercepted over unencrypted transport.
- **Booking spam / abuse**: automated public booking form used to flood the calendar or abuse email sending.
- **SQL injection**: user-supplied input used to manipulate database queries.
- **License tampering**: operator modifies the signed license document to fake a valid status.
- **PII exposure**: customer data returned in API responses it should not appear in, or retained after a GDPR deletion request.
- **Secrets in version control**: `.env` file accidentally committed.

---

## 2. Authentication & Authorization

### Admin Authentication

- Email/password login only in MVP.
- Passwords hashed with **bcrypt** (minimum cost factor 12).
- Session established on successful login; session token stored in an **HttpOnly, Secure, SameSite=Strict** cookie.
- Sessions stored server-side (database or memory store); cookie contains only the session ID, not any user data.
- [ASSUMPTION: OAuth / SSO (Google, GitHub, etc.) is a post-MVP consideration and will not be implemented in v0.1.0.]

### RBAC Roles

| Role | Permissions |
|---|---|
| **owner** | Full access to all features, settings, billing, and user management |
| **admin** | Same as owner, except cannot access billing settings or manage the license key |
| **staff** | Can view and manage their own calendar and assigned bookings; cannot access settings, other staff data, or customer list |

Role assignments are stored in the `users` table. All API endpoints enforce role checks at the route/dependency layer (FastAPI `Depends`).

### Public Booking Page

- Completely unauthenticated; no customer login required.
- Rate-limited per IP address (see Section 9 — Abuse Prevention).
- Returns only the data necessary to render the booking form (available services, available time slots for the requested date range).
- Does not expose internal IDs, staff emails, or admin notes in its API responses.

---

## 3. CSRF Protection

- **Primary defense**: `SameSite=Strict` session cookie. Browsers will not send this cookie on cross-site requests, neutralising the most common CSRF attack vector.
- **Secondary defense**: explicit CSRF token required for all state-changing admin API endpoints (POST, PUT, PATCH, DELETE). The token is included in the response of the session establishment endpoint and must be sent as a request header (`X-CSRF-Token`).
- Public booking endpoints are exempt from CSRF token requirements (they are intentionally accessible from any origin) but are protected by rate limiting.

---

## 4. Input Validation

- All FastAPI request bodies and query parameters are validated using **Pydantic v2** models. Invalid input is rejected with a `422 Unprocessable Entity` response before reaching business logic.
- All database queries use **SQLAlchemy** ORM or Core with bound parameters. Raw string interpolation into SQL is prohibited. `text()` constructs must use `:param` placeholders — never f-strings or `%` formatting.
- File uploads (if any, post-MVP): validated for MIME type, extension, and maximum size before storage.
- User-supplied strings displayed in the frontend are escaped by the React/Next.js rendering layer. The backend does not perform HTML sanitisation on the assumption that the frontend will handle display safely.

---

## 5. GDPR / Data Protection

### Customer Soft-Delete

When a customer data deletion request is received:

1. A GDPR deletion is triggered by an admin via the admin UI (no automated customer-facing request flow in MVP).
2. The following fields in the `customers` table are **nulled**: `name`, `email`, `phone`, `notes`, `address` (any other PII fields).
3. The `gdpr_deleted_at` timestamp is set to the current UTC time.
4. Booking records associated with the customer are **retained** (financial/operational records). The customer FK remains; the customer row becomes an anonymised placeholder.
5. The soft-deleted customer row is excluded from all normal query results via a default filter.
6. An audit log entry is written (actor: admin user, event: `customer.gdpr_deleted`).

This approach preserves booking history for operational and legal purposes while removing personal identifiers.

### Data Minimisation

- Only data strictly necessary for booking management is collected from customers: name, email, phone (optional), and any service-specific fields defined by the operator.
- No tracking cookies, analytics pixels, or third-party scripts on the public booking page in the default installation.

### Data Export

- Admins can request a data export for a specific customer (JSON or CSV format).
- The export includes all stored PII and associated booking records.
- [ASSUMPTION: A structured customer-facing "right of access" request portal is a post-MVP feature. In MVP, the admin manually handles requests.]

### SMTP Credentials

- SMTP credentials (host, port, username, password) entered via the admin settings UI are stored **encrypted** in the `settings` table using AES-256-GCM (key derived from `SECRET_KEY`).
- They are never returned in plaintext via API responses; the password field is masked in settings GET responses.

### Privacy Notice

- If the operator enables customer email collection, the booking form must display a privacy notice (configurable text field in admin settings).
- [ASSUMPTION: Servario ships with a default placeholder text; the operator is legally responsible for providing an accurate privacy notice for their jurisdiction.]

---

## 6. License Validation Security

### Ed25519 Signature

- Each license document is a JSON payload signed with the vendor's Ed25519 private key.
- The corresponding **public key is compiled into the backend binary** (embedded in source). It is not a secret, but it is not trivially replaceable without modifying and recompiling the source.
- On validation, the backend verifies the signature over the canonical JSON payload. If the signature does not match, the license status is set to `invalid` — it is never treated as valid or degraded.

### "Invalid" Status: No Demo/Eval Fallback

- A license with status `invalid` (failed signature check, corrupted payload, or missing required fields) does **not** fall back to Demo mode or any other reduced-functionality mode.
- An invalid signature is treated as a security signal: the license document may have been tampered with.
- The system will show a clear error in the admin UI and will block booking creation until a valid license is provided.

### Public Key Handling

- The Ed25519 public key is stored as a constant in the backend source code (`backend/app/license/public_key.py`).
- It is not read from the filesystem, environment variables, or the database at runtime.
- Replacing the public key requires modifying the source and rebuilding the container — which is permitted under the BUSL-1.1 license terms for self-hosted operators, but voids the integrity guarantee.

### RevenueCat Key Isolation

- RevenueCat API secret keys are **never present** in the self-hosted Servario instance, its `.env` file, or its container images.
- All RevenueCat interactions happen exclusively in the private **License Broker** service, which is operated by the vendor.
- The self-hosted instance only holds the signed license document (as a static artifact) and communicates with the License Broker's validation endpoint.

### License Validation Payload

When the self-hosted backend performs an online license validation call, it transmits **only**:

| Field | Description |
|---|---|
| `license_id` | UUID from the license document |
| `instance_id` | Locally generated UUID (see Section 11 of `07_selfhosting_devops.md`) |
| `product_version` | Semver string of the installed Servario version |
| `domain` | Optional: the operator's configured public domain |

**Never transmitted**: customer data, booking data, staff data, hardware identifiers, IP addresses beyond what is inherent in the HTTP request.

---

## 7. Secrets Management

### Required Secrets (Environment Variables)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Used for session cookie signing and SMTP credential encryption. Must be a cryptographically random string of ≥ 32 bytes. |
| `DATABASE_URL` | Full PostgreSQL connection URL including credentials. |
| `SMTP_PASSWORD` | If pre-seeded via env; otherwise stored encrypted in DB. |
| `SERVARIO_LICENSE_KEY` | The base64-encoded signed license JSON document. |

### Rules

- All secrets are provided via **environment variables** or Docker secrets. They are never hardcoded in source files.
- `.env` files must be listed in `.gitignore`. A `.env.example` file with placeholder values is committed to the repository.
- The application will refuse to start if `SECRET_KEY` is set to the example/default value in a production environment (`ENVIRONMENT=production`).
- No RevenueCat API keys exist in the self-hosted instance environment under any circumstances.
- Logs must never emit secrets. FastAPI exception handlers and logging formatters must redact the `DATABASE_URL` and `SECRET_KEY` values.

---

## 8. Audit Log

### Table Structure

The `audit_logs` table is **append-only**: no `UPDATE` or `DELETE` operations are ever issued against it by application code. Database-level enforcement (row-level security or a trigger) is recommended as a defence-in-depth measure.

### Logged Events

| Event Type | Actor |
|---|---|
| `booking.created` | `public` or `staff` |
| `booking.modified` | `staff` or `admin` |
| `booking.cancelled` | `staff`, `admin`, or `public` (if self-cancel is implemented) |
| `booking.confirmed` | `staff` or `admin` |
| `customer.gdpr_deleted` | `admin` |
| `admin.login` | `user` |
| `admin.logout` | `user` |
| `admin.login_failed` | `system` (no user_id) |
| `settings.changed` | `admin` |
| `license.status_changed` | `system` |
| `user.created` | `owner` |
| `user.role_changed` | `owner` |

### Log Entry Fields

```
id            UUID (primary key)
event_type    string (e.g. "booking.created")
actor_type    enum: user | system | public
actor_id      UUID or null (user_id for authenticated actors)
target_type   string (e.g. "booking", "customer")
target_id     UUID or null
metadata      JSONB (event-specific context, no full PII)
created_at    timestamptz (set by DB default, not application code)
```

### Integrity

- No audit log entries are modified or deleted by application code or admin UI.
- The admin UI can display audit log entries in read-only views.
- [ASSUMPTION: Cryptographic chaining of audit log entries (hash chain) is a post-MVP hardening measure.]

---

## 9. Abuse Prevention

### Public Booking Page

- **Rate limit**: maximum **10 booking submission attempts per IP address per 15-minute window**. Exceeding this returns `429 Too Many Requests`.
- Implementation: in-process counter using a sliding window (backed by Redis if available post-MVP; in-memory dict in MVP with TTL cleanup).
- The rate limit applies to the booking submission endpoint, not to the availability query endpoints (to allow normal calendar browsing).

### Spam Email Protection

- Maximum **3 booking confirmation emails sent to the same email address per 24-hour period**.
- This prevents the system from being used as an email spam relay against a target address.

### Admin Login

- **Rate limit**: maximum **10 failed login attempts per IP address per 15-minute window**.
- **Account lockout**: after **5 consecutive failed login attempts** for a specific email address, that account is temporarily locked for 15 minutes regardless of source IP.
- Lockout events are written to the audit log.

---

## 10. Dependency Security

- **Python**: all dependencies pinned with exact versions and hashes in `requirements.txt` generated by `pip-compile --generate-hashes`.
- **Node.js**: `package-lock.json` committed and enforced via `npm ci` in CI.
- **Automated updates**: Dependabot or Renovate configured to open PRs for dependency updates. Security advisories are treated as P1.
- `eval()` and `exec()` are prohibited in application code. Dynamic code execution from any user-supplied input is explicitly forbidden.
- Python security linting via **bandit** in CI (see `08_testing_quality.md`).

---

## 11. HTTPS Enforcement

- **Nginx Proxy Manager** (the default reverse proxy) handles TLS termination and automatic HTTPS via Let's Encrypt.
- The FastAPI backend and Next.js frontend containers are **never exposed on ports 80 or 443** directly in the production Docker Compose configuration. They communicate only over the internal Docker network.
- The backend sets the `X-Forwarded-Proto` trust configuration appropriately so that redirect responses use `https://`.
- **HSTS header** (`Strict-Transport-Security: max-age=31536000; includeSubDomains`) is added by the reverse proxy configuration. Operators should not disable this header.
- The application will log a warning (not a hard failure) if it detects it is receiving plaintext HTTP requests in a production environment, suggesting misconfiguration.

---

## 12. Known Limitations

This section is intentionally candid about security trade-offs inherent in the self-hosted, source-available model.

| Limitation | Impact | Rationale |
|---|---|---|
| **License checks can be removed by a technically skilled operator** | Revenue loss for the vendor; not a safety/data risk | Inherent trade-off of source-available software. BUSL-1.1 prohibits this commercially, but cannot technically prevent it. |
| **Single-instance model: no tenant isolation** | All data on the instance is accessible to any admin-level user | Servario is designed for a single organisation. Multi-tenancy is out of scope. |
| **No MFA in MVP** | Admin accounts protected only by password + rate limiting | [ASSUMPTION: TOTP-based MFA is a post-MVP feature.] |
| **In-memory rate limiting in MVP** | Rate limits reset on container restart; can be bypassed by attackers who trigger restarts | Acceptable for MVP; Redis-backed rate limiting planned post-MVP. |
| **Offline license grace period** | Up to 30 days of operation possible after license server becomes unreachable | Intentional UX trade-off to support air-gapped and unreliable network environments. |
