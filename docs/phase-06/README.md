## Phase 6 — Human Approval Workflow

SupportOps now includes an explicit human review step before a drafted response can move
forward.

Endpoints:

- `POST /api/v1/tickets/{ticket_id}/approve`
- `POST /api/v1/tickets/{ticket_id}/reject`

Approval behavior:

- only tickets in `waiting_review` can be reviewed
- an agent can approve the generated draft as-is
- an agent can replace the draft with a human-edited final response
- reviewer identity, note, and timestamp are persisted
- approved tickets move to `approved`
- rejected tickets move to `rejected`
- repeated review attempts are rejected with a conflict response

Stored review metadata:

- approved reply
- reviewed by
- review note
- reviewed timestamp
- final review status

This phase creates a clear human-in-the-loop boundary between AI-assisted drafting and the
later delivery/automation layer.
