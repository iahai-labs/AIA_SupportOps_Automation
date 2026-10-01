# Phase 10 — Production-safe Deployment

This phase prepares SupportOps for a low-cost public portfolio deployment without exposing
the application database or external integrations directly.

## Production topology

- PostgreSQL stays on the internal Compose network
- the application binds only to `127.0.0.1:8003`
- the existing host Nginx reverse proxy should publish the application under a HTTPS path
- the public demo runs in safe mode by default
- external AI and n8n calls are disabled unless explicitly enabled
- container health checks are included
- the app runs as a non-root container user

## Demo-safe defaults

`docker-compose.prod.yml` sets:

- `DEMO_SAFE_MODE=true`
- `DEMO_ALLOW_EXTERNAL_AI=false`
- `DEMO_ALLOW_EXTERNAL_AUTOMATION=false`

This keeps the portfolio demo deterministic and avoids accidental API cost or outbound workflow
execution.

## Database bootstrap

For a fresh portfolio deployment the application initializes the current SQLAlchemy schema at
startup. Before treating the project as a long-lived production system, replace bootstrap-only
schema creation with versioned Alembic migrations.

## Suggested reverse-proxy path

A suitable portfolio route is:

`https://ai.iradhd.ir/supportops/`

The host Nginx should proxy that path to:

`http://127.0.0.1:8003/`

Path-prefix proxy validation is required before the final release because the demo currently uses
root-relative `/static` and `/api` URLs.
