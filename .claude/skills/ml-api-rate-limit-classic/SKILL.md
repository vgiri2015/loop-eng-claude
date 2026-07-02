---
name: ml-api-rate-limit-classic
description: Diagnose and resolve ML/LLM API 429 rate-limit incidents using a single end-to-end troubleshooting workflow.
---

# ML API Rate Limit (Traditional Skill)

A single, self-contained troubleshooting workflow for ML/LLM API 429
rate-limit incidents. Gather evidence, determine the root cause, mitigate,
verify, and write the RCA — all in one pass.

---

## Trigger Conditions

Use this skill when any of the following are present:

- HTTP 429
- Too Many Requests
- Rate limit exceeded
- Quota exceeded
- Token limit exceeded
- Burst limit exceeded
- Throttling
- Retry-After header present
- API requests failing due to capacity or usage limits

---

## Primary Workflow

If `status == 429`, execute the following workflow.

---

## 1. Gather Evidence

Check and summarize the following signals.

### Request Rate

Verify:
- Requests per second
- Requests per minute
- Traffic increase compared to baseline
- Sudden spike or gradual growth

### Burst Rate

Verify:
- Peak traffic in short windows
- Concurrent request bursts
- Batch jobs or cron jobs causing spikes
- Traffic pattern around failure time

### Token Usage

Verify:
- Input tokens per request
- Output tokens per request
- Tokens per minute
- Token quota exhaustion
- Large prompts or long completions

### API Key

Verify:
- Correct API key is used
- Key is active
- Key belongs to expected workspace/project
- Key has correct tier/quota
- Key is not shared across multiple services unexpectedly

### Retry Logic

Verify:
- Retry count
- Retry interval
- Exponential backoff
- Jitter
- Whether retries respect `Retry-After`
- Whether failed requests are creating retry storms

### Queue Depth

Verify:
- Pending request queue size
- Queue growth rate
- Worker backlog
- Whether requests are being drained or accumulating

### Timeout

Verify:
- Client timeout setting
- Server timeout behavior
- Whether timeouts trigger duplicate retries
- Whether long-running calls are blocking workers

### Parallel Workers

Verify:
- Number of concurrent workers
- Thread count
- Async task count
- Autoscaling behavior
- Whether concurrency exceeds allowed quota

### Streaming Calls

Verify:
- Number of active streaming responses
- Long-lived connections
- Streaming timeout
- Whether streams are consuming quota longer than expected

### Regional Endpoint

Verify:
- Endpoint region
- Regional traffic routing
- DNS changes
- Failover behavior
- Whether throttling is isolated to one region

### SDK Version

Verify:
- SDK version
- Known retry behavior
- Known rate-limit bugs
- Recent SDK upgrade or downgrade
- Custom HTTP client behavior

### Known Incidents

Verify:
- Provider status page
- Internal incident tracker
- Recent provider degradation
- Regional incidents
- Capacity-related announcements

### Customer Tier

Verify:
- Current plan or quota tier
- Allowed request rate
- Allowed token rate
- Burst capacity
- Recent quota changes

### Usage History

Verify:
- Normal usage baseline
- Usage trend over last 24 hours
- Usage trend over last 7 days
- Recent traffic growth
- New workloads or deployments

---

## 2. Determine Root Cause

Analyze the evidence and classify the most likely root cause.

Possible root causes:
- Request rate exceeded
- Burst traffic exceeded
- Token-per-minute limit exceeded
- Shared API key causing unexpected aggregate usage
- Retry storm
- Queue backlog
- Excessive parallelism
- Streaming calls holding capacity
- Customer tier quota too low
- Regional throttling
- SDK retry behavior issue
- Provider-side incident
- Recent deployment increased traffic
- Misconfigured timeout causing duplicate requests

Return:

```text
Most Likely Root Cause:
Confidence:
Supporting Evidence:
Contributing Factors:
Missing Evidence:
```

---

## 3. Recommend Mitigation

Given the root cause, recommend the safest immediate mitigation first,
then the long-term remediation.

Immediate mitigation (stop the bleeding):
- Enable exponential backoff with jitter
- Respect the `Retry-After` header
- Reduce parallel workers / concurrency
- Cap and deduplicate retries; add a circuit breaker
- Queue and rate-shape incoming requests
- Fail over or spread load across regional endpoints

Long-term remediation (prevent recurrence):
- Standardize the retry policy across all callers
- Add a client-side rate limiter (request- and token-aware)
- Smooth bursty producers (batch jobs, cron, cache-expiry stampedes)
- Lower `max_tokens` / trim context for token-bound workloads
- Add multi-region routing with per-region concurrency caps
- Request a quota or tier increase when client-side fixes are insufficient

Escalate (tier increase, provider ticket) only when client-side fixes
cannot resolve the incident.

---

## 4. Verify Recovery

The fix is not "done" until the signals prove recovery. Confirm:
- 429 errors are decreasing
- Retries are succeeding
- Latency is stable
- The queue is draining
- The customer has confirmed recovery

If any check fails, return to step 1 with the new evidence.

---

## 5. Write the RCA

Produce a short root-cause analysis:

```text
Incident:
Root Cause:
Immediate Mitigation Applied:
Long-Term Remediation:
Verification Result:
Prevention:
```

---

## Final Response Format

The final response must include, in this order:

1. Incident Type
2. Root Cause
3. Evidence
4. Immediate Mitigation
5. Long-Term Remediation
6. Verification Plan
7. RCA
8. Prevention Plan
9. Missing Information
