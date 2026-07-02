# Playbook: Burst Traffic Exceeded Quota

## Summary
Short spikes push the request or token rate above the account's per-minute
limit even though the *average* rate is well under quota. The provider throttles
the burst, not the sustained load.

## Confirming Signals
- 429s cluster in tight bursts, then clear on their own.
- Peak request rate ≫ average request rate (spiky, not flat).
- `Retry-After` values are small (seconds), not minutes.
- No corresponding auth errors or 5xx.
- Traffic spikes align with a batch job, cron, cache expiry, or fan-out.

## Refuting Signals
- 429s are continuous and flat → look at [[token_quota]] or a low tier.
- 429 volume grows with retries → [[retry_storm]].
- Only one region is throttled → [[regional_throttling]].

## Immediate Mitigation
- Enable exponential backoff **with jitter** so retries de-synchronize.
- Respect the `Retry-After` header exactly.
- Introduce a client-side token-bucket rate limiter set below the account
  burst ceiling.

## Long-Term Remediation
- Rate-shape / queue bursty producers (batch jobs, fan-out).
- Smooth cron and cache-expiry stampedes with jitter.
- Request a higher burst allowance or tier increase if smoothing is infeasible.

## Verification
- Peak request rate stays under the burst ceiling.
- 429 bursts no longer recur after the smoothing change.
