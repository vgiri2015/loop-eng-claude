---
name: ml-api-rate-limit
description: Diagnose and resolve ML/LLM API 429 rate-limit incidents using loop engineering.
---

# ML API Rate Limit Skill

Use this skill when the case includes any of:
- HTTP 429
- Too Many Requests
- Rate limit exceeded
- Quota exceeded
- Token limit exceeded
- Throttling
- `Retry-After` header

## Architecture

This skill is an **orchestrator**, not a monolith. It coordinates a series of
focused reasoning loops. Each loop owns exactly one decision and returns a
structured result that the next loop consumes.

- `SKILL.md`      — entry point / router (this file)
- `loops/`        — focused reasoning steps, one decision each
- `playbooks/`    — domain knowledge per root cause
- `scripts/`      — deterministic evidence collectors
- `evals/`        — regression tests against historical cases

## Execution Contract

Run the case through these loops **in order**. Do not skip ahead. Each loop
must complete and emit its structured output before the next begins.

1. `loops/01_classify.md`        — Is this really a rate-limit incident?
2. `loops/02_collect_context.md` — Gather only the evidence needed to diagnose.
3. `loops/03_diagnose.md`        — Rank the most likely root causes.
4. `loops/04_mitigate.md`        — Choose the safest immediate mitigation.
5. `loops/05_verify.md`          — Confirm the incident is actually resolving.
6. `loops/06_learn.md`           — Convert the outcome into reusable knowledge.

**Do not jump directly to remediation** unless customer impact is active and
severity is P1/P0. Even then, run classification first.

When a root cause is identified, consult the matching file in `playbooks/`
for domain-specific guidance before finalizing mitigation.

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
