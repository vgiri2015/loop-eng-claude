# Playbook: Retry Storm

## Summary
A transient throttle triggers aggressive client retries. The retries add load,
which causes more 429s, which trigger more retries. The client amplifies the
incident it is trying to recover from.

## Confirming Signals
- 429 count *increases* after the first throttle instead of settling.
- Retries fire immediately or on a fixed short interval (no backoff, no jitter).
- Request rate climbs sharply right after the first 429.
- Many retries share identical or near-identical timestamps (synchronized).
- Total attempts ≫ unique logical requests.

## Refuting Signals
- Retries already use exponential backoff + jitter and volume is flat →
  look at [[burst_quota]] or [[token_quota]].
- Throttling is isolated to one region → [[regional_throttling]].

## Immediate Mitigation
- Cap max retry attempts (e.g. 3–5) and add a circuit breaker.
- Switch to exponential backoff **with jitter**; honor `Retry-After`.
- Temporarily reduce concurrency to break the amplification loop.

## Long-Term Remediation
- Standardize retry policy across all callers (one shared client config).
- Make retries idempotent and deduplicated.
- Add a global concurrency limiter so retries cannot outrun capacity.

## Verification
- 429 count decays after mitigation instead of growing.
- Retry attempts per logical request return to ~1.
- No synchronized retry bursts in the logs.
