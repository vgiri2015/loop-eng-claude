# Loop 2: Context Collection

## Goal
Collect only the evidence needed for diagnosis. Do not diagnose yet.

## Required Signals
- Request rate
- Burst rate
- Token usage
- API key
- Retry logic
- Queue depth
- Timeout
- Parallel workers
- Streaming calls
- Regional endpoint
- SDK version
- Known incidents
- Customer tier
- Usage history

## How to Collect
Prefer deterministic collectors over guessing:
- Run `scripts/collect_api_metrics.py` for request/burst/token/usage signals.
- Run `scripts/parse_429_logs.py` to extract 429 timestamps and `Retry-After`.
- Fall back to the ticket only for signals the scripts cannot provide.

Mark any signal you cannot obtain as missing rather than inventing a value.

## Output
Return:

```json
{
  "available_evidence": {},
  "missing_evidence": [],
  "diagnosis_ready": true
}
```

Set `diagnosis_ready` to `false` if a signal critical to diagnosis (request
rate, burst rate, or token usage) is missing.
