# Loop 4: Mitigation

## Goal
Given the diagnosed root cause, choose the **safest** immediate mitigation and
the long-term remediation. Do not rediscover the diagnosis.

## Input
The diagnosis object from Loop 3 and the matching `playbooks/*.md`.

## Guidance
- Prefer reversible, low-blast-radius actions first (backoff, respect
  `Retry-After`, reduce parallelism).
- Separate **immediate mitigation** (stop the bleeding) from **long-term
  remediation** (prevent recurrence).
- Only recommend escalation (tier increase, provider ticket) when client-side
  fixes cannot resolve the incident.

## Common Mitigations
- Enable exponential backoff with jitter
- Respect the `Retry-After` header
- Reduce parallel workers / concurrency
- Queue and rate-shape incoming requests
- Spread load across regional endpoints
- Request a quota / tier increase

## Output
Return:

```json
{
  "immediate_mitigation": [],
  "long_term_remediation": [],
  "requires_escalation": false,
  "escalation_reason": ""
}
```
