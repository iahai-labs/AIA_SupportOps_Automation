## Phase 3 — Priority & SLA Engine

Support priority is now determined by a deterministic rules engine after ticket classification.

The LLM does not own the final SLA decision. Classification signals are converted into
explicit priority and response targets through testable business rules.

Current policy:

- urgent urgency → urgent priority → 1-hour SLA
- high urgency → high priority → 4-hour SLA
- low urgency → low priority → 24-hour SLA
- billing/account + normal urgency → normal priority → 8-hour SLA
- technical + normal urgency → normal priority → 6-hour SLA
- other normal/unknown cases → normal priority → 12-hour SLA

Each ticket stores:

- priority
- SLA duration in hours
- SLA due timestamp
- human-readable priority reason

This keeps support prioritization explainable, auditable, and independent of LLM behavior.
