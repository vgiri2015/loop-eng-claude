# Loop 5: Verification

## Goal
Confirm the incident is actually resolving. A fix is not "done" until the
signals prove recovery.

## Checks
- Are 429 errors decreasing?
- Are retries succeeding?
- Is latency stable?
- Is the queue draining?
- Has the customer confirmed recovery?

## Method
Re-run `scripts/collect_api_metrics.py` after the mitigation window and compare
against the pre-mitigation baseline captured in Loop 2.

## Output
Return:

```json
{
  "resolved": false,
  "checks": {
    "429_decreasing": null,
    "retries_succeeding": null,
    "latency_stable": null,
    "queue_draining": null,
    "customer_confirmed": null
  },
  "next_action": ""
}
```

If `resolved` is `false`, set `next_action` and loop back to Diagnosis (Loop 3)
with the new evidence.
