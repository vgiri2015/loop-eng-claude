# Loop 1: Incident Classification

## Goal
Decide whether this is truly an ML/LLM API rate-limit incident. Nothing else
happens in this loop — no diagnosis, no mitigation, no RCA.

## Input
Customer ticket, logs, error codes, API responses, request IDs.

## Decision Criteria
Classify as a rate-limit incident if the evidence includes any of:
- HTTP 429
- `Retry-After` header
- "quota exceeded" message
- "token limit exceeded" message
- throttling response

If the evidence points elsewhere (5xx, auth errors, timeouts unrelated to
throttling), classify accordingly and stop — this skill does not apply.

## Severity Guidance
- **P0/P1** — active, widespread customer impact; production traffic failing.
- **P2**     — partial impact or degraded throughput.
- **P3**     — intermittent or single-tenant, no material impact.

## Output
Return only:

```json
{
  "incident_type": "",
  "subtype": "",
  "severity": "",
  "confidence": 0,
  "reason": ""
}
```
