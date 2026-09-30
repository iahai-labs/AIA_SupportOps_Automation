## Phase 4 — Knowledge Retrieval

SupportOps now includes a lightweight knowledge retrieval layer.

Current capabilities:

- knowledge article model and ingestion endpoint
- category-aware retrieval
- deterministic lexical ranking
- source references
- relevance score per match
- retrieval confidence
- safe empty-result behavior
- ticket-specific retrieval endpoint

Endpoints:

- `POST /api/v1/knowledge`
- `GET /api/v1/tickets/{ticket_id}/knowledge`

This phase intentionally uses a small deterministic retrieval implementation rather than
duplicating the full RAG stack from the Business Knowledge Assistant project.

The retrieval service is isolated behind a dedicated module so embedding/vector search can
be introduced later without changing the support workflow contract.

Phase 5 will use the retrieved context to generate grounded reply drafts.
