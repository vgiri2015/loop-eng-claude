# Loop 3: Diagnosis

## Goal
Determine the most likely root cause. Rank hypotheses by confidence. Do **not**
recommend mitigation here — that is Loop 4's job.

## Input
The `available_evidence` object from Loop 2.

## Possible Root Causes
- Burst traffic exceeded quota
- Token-per-minute limit exceeded
- Retry storm
- Shared API key contention
- Excessive parallelism
- Queue backlog
- Streaming calls holding capacity
- Regional throttling
- SDK retry behavior issue
- Provider-side incident
- Customer tier too low

## Method
1. Match evidence patterns against the candidates above.
2. Consult the matching `playbooks/*.md` file for confirming/refuting signals.
3. Rank hypotheses; note what additional evidence would raise or lower each.

## Output
Return:

```json
{
  "top_root_cause": "",
  "confidence": 0,
  "ranked_hypotheses": [],
  "supporting_evidence": [],
  "missing_evidence": []
}
```
