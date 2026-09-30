## Phase 7 — Automation / n8n / Notifications

Approved support tickets can now cross an explicit outbound automation boundary.

Current capabilities:

- n8n webhook integration
- optional `X-AIA-Webhook-Secret`
- bounded delivery attempts
- persisted automation status
- persisted attempt count and last error
- structured approved-ticket payload
- email notification recommendation
- Telegram recommendation for high/urgent tickets

Environment variables:

- `N8N_WEBHOOK_URL`
- `N8N_WEBHOOK_SECRET`
- `AUTOMATION_TIMEOUT_SECONDS`
- `AUTOMATION_MAX_ATTEMPTS`

Behavior:

- if no webhook is configured, delivery is safely marked `skipped`
- approved tickets trigger the automation boundary
- rejected tickets do not trigger outbound delivery
- automation failure does not undo the human approval decision
- delivery state remains visible on the ticket for later audit/retry work
