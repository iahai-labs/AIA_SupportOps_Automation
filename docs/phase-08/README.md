# Phase 8 — Audit & Reliability

This phase adds operational traceability and safer automation retry behavior.

## Added

- persistent ticket audit events
- lifecycle event recording for ticket creation, reply drafting, review, automation delivery, and retries
- `GET /api/v1/tickets/{ticket_id}/audit`
- `POST /api/v1/tickets/{ticket_id}/automation/retry`
- retry-state guard
- idempotency protection for already-sent automation
- cumulative retry attempt accounting
- conflict responses for non-retryable states

Automation retry is allowed only for approved tickets whose automation state is `failed` or `skipped`.
The human approval decision is never rolled back by automation failure.
