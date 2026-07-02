# Playbook: Regional Throttling

## Summary
Throttling is scoped to a single region or endpoint rather than the account as a
whole. Account-wide quota may be fine, but one regional endpoint is saturated or
degraded.

## Confirming Signals
- 429s concentrate on one regional endpoint; other regions are healthy.
- Account-wide request and token rates are under quota.
- May coincide with a provider status note for that region.
- Latency on the affected region is elevated alongside the 429s.

## Refuting Signals
- All regions throttle equally → [[burst_quota]] or [[token_quota]].
- 429s scale with retries across regions → [[retry_storm]].

## Immediate Mitigation
- Fail over or spread load to healthy regional endpoints.
- Respect `Retry-After` for the affected region.
- Temporarily lower concurrency against the degraded region.

## Long-Term Remediation
- Add multi-region routing with health-aware load balancing.
- Set per-region concurrency caps.
- Subscribe to provider status/incident feeds and automate failover.

## Verification
- 429s on the affected region clear after rerouting.
- Latency on that region returns to baseline.
- Load is balanced across healthy regions.
