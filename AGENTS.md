# Agent Instructions

This repository implements **Loop Engineering**: a tiny orchestrator that runs a
series of focused reasoning loops, each owning exactly one decision.

## When to use

For any ML/LLM API **HTTP 429 / rate-limit / quota-exceeded / throttling**
incident, execute the `ml-api-rate-limit` skill.

## How to execute

Read `.claude/skills/ml-api-rate-limit/SKILL.md`, then run the loops in
`.claude/skills/ml-api-rate-limit/loops/` strictly in order (01 → 06).

Rules:

- Complete **one loop at a time**. Emit that loop's structured (JSON) output
  before starting the next. Do **not** jump ahead to mitigation or RCA.
- Feed each loop's output as the input to the next loop.
- When a root cause is identified, consult the matching file in
  `.claude/skills/ml-api-rate-limit/playbooks/`.
- Gather evidence with the deterministic collectors instead of guessing:
  - `.claude/skills/ml-api-rate-limit/scripts/collect_api_metrics.py`
  - `.claude/skills/ml-api-rate-limit/scripts/parse_429_logs.py`
  Mark anything you cannot measure as missing rather than inventing values.
- After Loop 6, produce the **Final Response Format** defined in `SKILL.md`.

The loops are:

1. `01_classify.md` — Is this really a rate-limit incident?
2. `02_collect_context.md` — Gather only the evidence needed to diagnose.
3. `03_diagnose.md` — Rank the most likely root causes.
4. `04_mitigate.md` — Choose the safest immediate mitigation.
5. `05_verify.md` — Confirm the incident is actually resolving.
6. `06_learn.md` — Convert the outcome into reusable knowledge.

## Scripts

Python 3, no dependencies. See `README.md` for usage examples.
