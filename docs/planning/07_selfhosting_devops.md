# 07 — Self-Hosting & DevOps

> Status: Planning / Pre-Implementation
> Audience: DevOps / Selfhosting Architect, operators
> Language: English

---

## Design Principles

- **Docker Compose first**: one command to start, one command to update
- **Low operational complexity**: runs on a €5/month VPS with 1 vCPU and 512 MB RAM
- **No Kubernetes required**: target audience is self-hosters, not platform engineers
- **Updatable without data loss**: migrations run automatically on startup
- **License-aware configuration**: `SERVARIO_LICENSE_KEY` is a first-class env var; no RevenueCat keys in the instance

---

## Minimum Server Requirements

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 1 vCPU | 2 vCPU |
| RAM | 512 MB | 1 GB |
| Disk | 5 GB | 20 GB |
| OS | Ubuntu 22.04 LTS or Debian 12 | Same |
| Docker | Engine 24+ | Latest stable |
| Docker Compose | v2 (plugin, not standalone) | Latest stable |

---

## Docker Compose Architecture

### Services

| Service | Image | Role |
|---|---|---|
| `db` | `postgres:15-alpine` | PostgreSQL database |
| `backend` | `servario/backend:latest` | FastAPI application |
| `frontend` | `servario/frontend:latest` | Next.js application |
| `proxy` | `jc21/nginx-proxy-manager:latest` | Reverse proxy + auto-HTTPS |

Post-MVP optional:
| Service | Image | Role |
|---|---|---|
| `redis` | `redis:7-alpine` | Celery broker (if APScheduler is replaced) |
| `worker` | `servario/backend:latest` | Celery worker |

### Networks

```yaml
networks:
  internal:        # db, backend, frontend — not exposed
  proxy:           # proxy only — exposed on 80/443
```

### Volumes

| Volume | Contents |
|---|---|
| `postgres_data` | PostgreSQL data files |
| `npm_data` | Nginx Proxy Manager config, SSL certificates |
| `servario_data` | License file (`license.json`), instance ID, uploaded assets |

---

## .env.example (Full Reference)

```env
# ─── Database ────────────────────────────────────────────────────────────────
POSTGRES_DB=servario
POSTGRES_USER=servario
POSTGRES_PASSWORD=change_me_in_production
DATABASE_URL=postgresql+asyncpg://servario:change_me_in_production@db:5432/servario

# ─── Application ─────────────────────────────────────────────────────────────
SECRET_KEY=change_me_to_a_long_random_string_at_least_32_characters
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com

# ─── License ─────────────────────────────────────────────────────────────────
# base64-encoded Ed25519-signed license JSON — obtain from the Servario license portal
SERVARIO_LICENSE_KEY=

# Optional: URL of the Servario License Broker for online validation
# Leave empty to use local-only validation (recommended for air-gapped deployments)
SERVARIO_LICENSE_SERVER_URL=

# Unique identifier for this installation — auto-generated on first start if empty
# Override for infrastructure-as-code consistency (e.g., Ansible, Terraform)
SERVARIO_INSTANCE_ID=

# Days of offline operation allowed before online validation is required (default: 30)
SERVARIO_LICENSE_OFFLINE_GRACE_DAYS=30

# ─── SMTP (can also be configured via admin UI after first start) ─────────────
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=noreply@example.com
# SMTP_PASSWORD=

# ─── Frontend ────────────────────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

**Important**: This file contains NO RevenueCat API keys, webhook secrets, or License Broker credentials. Those are exclusively for the License Broker service operated by the Servario vendor — they must never appear in the self-hosted instance.

---

## Reverse Proxy Options

### Default: Nginx Proxy Manager

Nginx Proxy Manager (NPM) is the recommended standard in the default `docker-compose.yml`.

**Why NPM:**
- Web-based GUI for managing proxy hosts (no config file editing)
- Automatic HTTPS via Let's Encrypt
- Docker-native: runs as a container
- Widely used and trusted in the self-hoster community
- Supports websockets, custom headers, and access lists

**Setup:**
1. Start the stack with `docker compose up -d`
2. Access NPM admin UI at `http://your-server-ip:81`
3. Create a proxy host pointing to the `frontend` container on port 3000
4. Create a proxy host pointing to `/api` → `backend` container on port 8000
5. Enable SSL with Let's Encrypt

### Alternative: Caddy

```caddyfile
yourdomain.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /* frontend:3000
}
```

Caddy handles automatic HTTPS without a GUI. Suitable for operators comfortable with config files.

### Alternative: Plain Nginx

Documented in `docs/deployment/nginx.md` [ASSUMPTION: separate deployment guide]. Suitable for advanced operators who manage certificates manually (e.g., with certbot).

### Alternative: Traefik

Docker-native with label-based configuration. Suitable for operators already running Traefik. Configuration documented separately [ASSUMPTION].

---

## Update Procedure

No data loss. Migrations run automatically on backend startup.

```bash
# Pull latest images and configuration
git pull origin main
docker compose pull

# Restart services (Alembic migrations run on backend startup)
docker compose up -d --remove-orphans
```

**Before updating to a new major version**: read the release notes for breaking changes and manual migration steps (if any).

---

## Database Migrations

- Tool: **Alembic** (Python migration framework for SQLAlchemy)
- Auto-applied on backend startup: `alembic upgrade head`
- Migration files are version-controlled in `backend/alembic/versions/`
- Preview SQL before applying: `alembic upgrade --sql head`
- Never modify existing migration files; always create new ones

**Backup before migrating**: always take a database backup before applying migrations to a production instance (see Backup Strategy below).

---

## Backup Strategy

### What to Back Up

| Data | Location | Method |
|---|---|---|
| PostgreSQL data | `postgres_data` Docker volume | `pg_dump` |
| License file | `servario_data` volume | File copy |
| Instance ID | `servario_data/instance_id` | File copy |
| `.env` file | Host filesystem | File copy |

### Recommended Schedule [ASSUMPTION]

| Frequency | Retention |
|---|---|
| Daily | 7 days |
| Weekly | 4 weeks |
| Monthly | 3 months (before major upgrades) |

### Example Backup Script

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/servario/backups

# PostgreSQL dump
docker compose exec -T db pg_dump -U servario servario \
  | gzip > "${BACKUP_DIR}/db_${DATE}.sql.gz"

# Data volume
docker run --rm \
  -v servario_servario_data:/data \
  -v "${BACKUP_DIR}:/backup" \
  alpine tar czf "/backup/data_${DATE}.tar.gz" /data

echo "Backup complete: ${DATE}"
```

Backup destination: outside the container host machine (e.g., S3-compatible storage, remote NFS, or a separate server).

---

## License File Handling

- **Primary**: `SERVARIO_LICENSE_KEY` environment variable (base64-encoded signed JSON)
- **Alternative**: `/data/license.json` (file in the `servario_data` volume)
- **Permissions**: `600` — readable only by the application process user
- **Instance ID**: auto-generated UUID on first start, persisted to `/data/instance_id`
  - Operator may set `SERVARIO_INSTANCE_ID` explicitly for reproducible deployments
  - Changing instance ID after license issuance may require license re-activation [ASSUMPTION]

---

## Health Endpoint

`GET /api/health`

Returns:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "connected",
  "license_status": "active"
}
```

The `license_status` field returns the current enum value (`active`, `grace`, `expired`, `missing`, `invalid`, `revoked`, `server_unreachable`). It does not return license details (no license_id, no customer_reference).

Use this endpoint with uptime monitoring tools (Uptime Kuma, Healthchecks.io, etc.).

---

## Monitoring

### Minimal Setup (Recommended for MVP)

- **Uptime Kuma**: self-hostable uptime monitor; poll `GET /api/health` every 60 seconds
- **Docker log driver**: default `json-file` with log rotation (`max-size: 10m`, `max-file: 3`)

### Advanced Setup (Post-MVP)

- Loki + Grafana for log aggregation and dashboards
- Prometheus metrics endpoint [ASSUMPTION: post-MVP]
- Alertmanager for license expiry and health alerts

---

## Security Hardening

### Container Security

- Run backend and frontend containers as non-root users (UID 1000)
- No `--privileged` flag
- Read-only filesystem for application containers where possible (writable `/tmp` and `/data` mounts only)
- No docker socket mounted into application containers

### Host Firewall (UFW example)

```bash
ufw default deny incoming
ufw allow ssh        # port 22
ufw allow http       # port 80
ufw allow https      # port 443
ufw enable
```

Database port (5432) must NOT be exposed to the public internet. It is accessible only on the internal Docker network.

### SSH

- Disable password authentication; use SSH keys only
- Consider fail2ban for SSH brute-force protection

---

## Release and Update Notifications [ASSUMPTION: Post-MVP]

- GitHub Releases for new versions
- Optional: `GET /api/admin/updates` endpoint that checks for a newer version
- Access to official Docker image registry may be gated by active license status (soft binding: encourages maintaining a valid license)

---

## Environment Variable Summary

| Variable | Default | Required | Notes |
|---|---|---|---|
| `POSTGRES_DB` | `servario` | Yes | |
| `POSTGRES_USER` | `servario` | Yes | |
| `POSTGRES_PASSWORD` | (none) | Yes | Must be changed from default |
| `DATABASE_URL` | (none) | Yes | Full async DSN |
| `SECRET_KEY` | (none) | Yes | Min. 32 random characters |
| `ENVIRONMENT` | `production` | Yes | `production` or `development` |
| `ALLOWED_ORIGINS` | (none) | Yes | Comma-separated list of allowed CORS origins |
| `SERVARIO_LICENSE_KEY` | (empty) | No | Empty = Demo/Eval mode |
| `SERVARIO_LICENSE_SERVER_URL` | (empty) | No | Empty = local-only validation |
| `SERVARIO_INSTANCE_ID` | (auto) | No | Auto-generated UUID on first start |
| `SERVARIO_LICENSE_OFFLINE_GRACE_DAYS` | `30` | No | Range 1–90 |
| `NEXT_PUBLIC_API_URL` | (none) | Yes | Public URL of the backend API |

**Not in this file**: RevenueCat keys, License Broker credentials, Ed25519 private key.

---

*All items marked `[ASSUMPTION]` require project owner confirmation before implementation.*
