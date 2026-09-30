## Phase 2 — AI Classification

Ticket intake now performs structured support classification before persistence.

Generated fields:

- category
- urgency
- language
- summary
- confidence
- classification source

Supported categories:

- billing
- technical
- sales
- account
- general
- unknown

The AI layer is isolated behind an OpenAI-compatible provider abstraction.
Groq-compatible configuration is supported by default.

If the AI provider is unavailable or no API key is configured, the application falls back
to deterministic classification so ticket intake continues instead of failing.

This phase intentionally does not assign final support priority yet. Priority/SLA logic is
handled separately in Phase 3.
