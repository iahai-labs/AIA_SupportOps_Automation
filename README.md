# AIA SupportOps Automation

[![CI](https://github.com/iahai-labs/AIA_SupportOps_Automation/actions/workflows/ci.yml/badge.svg)](https://github.com/iahai-labs/AIA_SupportOps_Automation/actions/workflows/ci.yml)

AI-assisted customer support operations with ticket intake, triage, SLA prioritization,
grounded reply drafting, human review, and workflow automation.

## Phase 1 — Ticket Intake Foundation

- FastAPI application
- PostgreSQL-ready persistence
- support ticket model
- validated ticket intake API
- ticket detail endpoint
- health endpoint
- pytest + Ruff
- Docker baseline
- GitHub Actions CI
- Dependabot
- SECURITY.md
- MIT license

## API

`POST /api/v1/tickets`

```json
{
  "customer_name": "Sarah Miller",
  "customer_email": "sarah@example.com",
  "subject": "Cannot access my account",
  "message": "I reset my password but I still cannot sign in."
}
```

`GET /api/v1/tickets/{ticket_id}`

`GET /health`

## Local Development

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

## Quality Gates

```bash
python -m ruff check .
python -m pytest -q
```

## Dependency & Tooling Files

- `requirements.txt` — pinned runtime/development dependencies for installation, Docker, local development, and CI.
- `pyproject.toml` — project metadata and pytest/Ruff configuration.

## Roadmap

- Phase 2 — AI Classification
- Phase 3 — Priority & SLA Engine
- Phase 4 — Knowledge Retrieval
- Phase 5 — Reply Drafting
- Phase 6 — Human Approval Workflow
- Phase 7 — Automation / n8n / Notifications
- Phase 8 — Audit & Reliability
- Phase 9 — Demo UI
- Phase 10 — Production-safe Deployment
- Phase 11 — GitHub Portfolio Hardening
- Phase 12 — Final Quality Gate + v1.0.0

## License

MIT — see [`LICENSE`](LICENSE).
