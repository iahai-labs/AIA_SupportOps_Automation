# Case Study — AIA SupportOps Automation

## Problem

Customer support operations are often slowed by repeated manual work:

- reading and classifying incoming tickets
- deciding urgency and SLA priority
- searching internal support knowledge
- drafting repetitive replies
- deciding whether a response is safe to send
- triggering follow-up workflows
- reconstructing what happened after the fact

A simple chatbot solves only the drafting problem. The larger operational problem is orchestration, control, and traceability.

## Constraints

The system was designed around several constraints:

- AI output cannot be assumed correct
- operational priority rules should remain deterministic
- replies should be grounded in approved support knowledge
- outbound automation should not bypass human review
- provider outages should degrade safely
- a public portfolio demo should not expose credentials or create uncontrolled API cost
- workflow state must remain inspectable after failures

## Decisions

### Separate AI from policy
Classification may be AI-assisted, but SLA and priority decisions live in deterministic application logic.

### Ground drafting in retrieved knowledge
The reply service receives verified support context and source references. Missing context produces a safe handoff rather than unsupported policy claims.

### Keep a human approval boundary
Draft generation does not automatically mean delivery. Reviewers can approve, edit, or reject the response before automation.

### Persist operational state
Classification, SLA, draft, review, automation result, and audit events are persisted so the workflow is observable.

### Make automation failure non-destructive
An outbound failure does not undo the approval decision. Retry state is tracked independently.

### Protect the public demo
The deployed demo uses safe mode, disables external AI/n8n execution by default, binds the application to localhost, and keeps PostgreSQL internal to Docker.

## Result

The finished workflow demonstrates:

- support-specific AI orchestration
- deterministic business rules
- grounded response generation
- explicit human-in-the-loop control
- auditability
- retry-safe automation
- production-oriented deployment
- CI-backed code quality
- a live interactive portfolio demo

The project therefore demonstrates more than a chatbot: it shows how AI can be inserted into a business workflow while preserving control, reliability, and traceability.
