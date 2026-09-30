## Phase 5 — Grounded Reply Drafting

SupportOps can now generate and persist reply drafts for support tickets.

Endpoint:

- `POST /api/v1/tickets/{ticket_id}/draft`

The draft pipeline:

1. loads the ticket
2. retrieves relevant support knowledge
3. generates a reply using only verified context
4. persists the draft and its metadata
5. moves the ticket to `waiting_review`

Stored reply metadata:

- draft reply text
- confidence
- source references
- generation source (`ai` or `fallback`)
- human-review requirement

Safety behavior:

- if no relevant knowledge is available, the system does not invent an answer
- instead, it generates a safe handoff message and marks the ticket for human review
- if the AI provider fails, the system uses a deterministic grounded fallback
- AI confidence is capped by retrieval confidence

This keeps reply generation grounded in support documentation rather than allowing the model
to make unsupported policy or technical claims.
