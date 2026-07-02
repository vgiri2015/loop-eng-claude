# Loop Engineering for Claude Skills

A reference implementation of **Loop Engineering** — an architecture for AI
support/automation systems that replaces one giant monolithic prompt with a
**tiny orchestrator** that coordinates a series of **focused reasoning loops**,
where each loop owns exactly one decision.

The worked example is an ML/LLM API **HTTP 429 rate-limit** troubleshooter.

> Prompt Engineering taught AI *what* to do.
> Workflow Engineering taught AI *how* to execute.
> **Loop Engineering** designs systems that reduce uncertainty one decision at
> a time — and learn from every outcome.

---

## What's in here

```
.claude/
  skills/
    ml-api-rate-limit/            # ← the loop-engineered skill
      SKILL.md                    #   entry point / router (orchestrator)
      loops/
        01_classify.md            #   Loop 1 — is this really a rate-limit incident?
        02_collect_context.md     #   Loop 2 — gather only the evidence needed
        03_diagnose.md            #   Loop 3 — rank the most likely root causes
        04_mitigate.md            #   Loop 4 — choose the safest mitigation
        05_verify.md              #   Loop 5 — confirm it's actually resolving
        06_learn.md               #   Loop 6 — turn the outcome into knowledge
      playbooks/                  #   domain knowledge, one file per root cause
        burst_quota.md
        retry_storm.md
        token_quota.md
        regional_throttling.md
      scripts/                    #   deterministic evidence collectors
        collect_api_metrics.py
        parse_429_logs.py
      evals/
        golden_429_cases.json     #   regression cases

    ml-api-rate-limit-classic/    # ← the traditional monolithic skill (for contrast)
      SKILL.md
```

- **`ml-api-rate-limit`** — the loop-engineered version. Small router + six loops.
- **`ml-api-rate-limit-classic`** — the same problem solved as one big
  self-contained `SKILL.md`, kept for side-by-side comparison.

---

## The core idea

Each loop is just a Markdown file that:

1. states **one goal** ("classify", "diagnose", …),
2. defines its **input** (the previous loop's structured output), and
3. returns a **structured output** the next loop consumes.

Because the loops are plain Markdown, **any coding agent can run them** — the
orchestration is just "read these files and execute them in order, one at a
time, without skipping ahead." The sections below show how to do that in each
tool.

### The universal execution prompt

This single instruction drives the loop engine in *any* assistant. Paste it,
or point the tool at the repo:

```
You are executing the "ml-api-rate-limit" skill using Loop Engineering.

Read .claude/skills/ml-api-rate-limit/SKILL.md, then run the loops in
.claude/skills/ml-api-rate-limit/loops/ strictly in order (01 → 06).

Rules:
- Complete ONE loop at a time. Emit that loop's structured output before
  starting the next. Do not jump ahead to mitigation or RCA.
- Feed each loop's output as the input to the next loop.
- When a root cause is identified, consult the matching file in playbooks/.
- Use scripts/collect_api_metrics.py and scripts/parse_429_logs.py to gather
  evidence instead of guessing; mark anything you can't measure as missing.
- After Loop 6, produce the Final Response Format from SKILL.md.

Here is the incident:
<paste the ticket / logs / error output here>
```

---

## Running it per tool

### Claude Code (native)

Skills in `.claude/skills/` are auto-discovered — no setup needed.

```bash
# from the repo root
claude
```

- **Automatic:** paste a ticket mentioning `429`, `rate limit`, `quota
  exceeded`, etc. and the skill triggers on its description.
- **Explicit:** invoke it by name:

  ```
  /ml-api-rate-limit Our app is getting HTTP 429 from the Claude API since 2am.
  ```

Claude Code reads `SKILL.md`, walks the loops in order, runs the `scripts/`,
and consults `playbooks/` automatically.

### Cursor

Cursor doesn't read `.claude/skills`, but the loops are plain Markdown, so
expose them as a **project rule** and reference the files in chat.

1. Create `.cursor/rules/loop-engineering.mdc`:

   ```mdc
   ---
   description: Run the ml-api-rate-limit skill via loop engineering
   alwaysApply: false
   ---
   When troubleshooting an HTTP 429 / rate-limit incident, execute the loops in
   `.claude/skills/ml-api-rate-limit/loops/` in order (01 → 06), one at a time,
   emitting each loop's structured output before the next. Consult
   `.claude/skills/ml-api-rate-limit/playbooks/` for the diagnosed root cause and
   use the `scripts/` to gather evidence. Finish with the Final Response Format
   in `SKILL.md`.
   ```

2. In Cursor chat (Agent mode), attach the files with `@` and paste the incident:

   ```
   @SKILL.md @loops  Run this as a loop-engineering incident:
   <paste ticket / logs>
   ```

Cursor also reads a root **`AGENTS.md`** if present (see below) — that works too.

### Windsurf (Cascade)

Use a **workflow** so you get a slash command, and/or a rule.

1. Create `.windsurf/workflows/rate-limit.md`:

   ```md
   ---
   description: Loop-engineered 429 rate-limit troubleshooter
   ---
   Execute the loops in `.claude/skills/ml-api-rate-limit/loops/` in order
   (01 → 06), one decision at a time, passing each loop's structured output to
   the next. Use `scripts/` to collect evidence, consult `playbooks/` for the
   root cause, and end with the Final Response Format from `SKILL.md`.
   ```

2. In Cascade, run it:

   ```
   /rate-limit
   <paste ticket / logs>
   ```

   (Or add the same guidance as a rule in `.windsurf/rules/`.)

### OpenAI Codex (CLI / IDE)

Codex reads **`AGENTS.md`** files for instructions. Add the universal execution
prompt there (an `AGENTS.md` is provided at the repo root — see below), then:

```bash
codex "Run the ml-api-rate-limit loops on this incident: <paste ticket/logs>"
```

Codex will follow `AGENTS.md`, read the loop files, and execute them in order.

### Google Antigravity

Antigravity's agent reads repo context and executes multi-step tasks. Point its
agent at the skill and hand it the incident:

```
Open .claude/skills/ml-api-rate-limit/SKILL.md and run the loops in loops/
sequentially (01 → 06), one decision per step. Use scripts/ for evidence and
playbooks/ for the root cause. Then produce the Final Response Format.

Incident: <paste ticket / logs>
```

Optionally save that as a reusable Workflow/Knowledge item in the Agent Manager
so it's one click next time.

### Any other agent / raw LLM

The loops are model- and tool-agnostic. Either:

- paste the **universal execution prompt** above plus the contents of `SKILL.md`
  and the six loop files into the chat, **or**
- run each loop as its own turn: paste `01_classify.md` + the incident, take the
  JSON it returns, paste `02_collect_context.md` + that JSON, and so on. Running
  loops as separate turns is the purest form of the pattern and keeps each
  reasoning step clean.

---

## `AGENTS.md`

A root [`AGENTS.md`](./AGENTS.md) mirrors the universal execution prompt so
tools that use the emerging `AGENTS.md` standard (Codex, Cursor, Windsurf, and
others) pick up the loop-engineering instructions automatically.

---

## Trying the scripts

The evidence collectors are standalone (Python 3, no dependencies):

```bash
# derive request rate, burst/peak rate, tokens/min from a metrics export
python3 .claude/skills/ml-api-rate-limit/scripts/collect_api_metrics.py samples.json

# extract 429 timing + Retry-After from logs
python3 .claude/skills/ml-api-rate-limit/scripts/parse_429_logs.py access.log --json

# verification compare (Loop 5): after vs. baseline
python3 .claude/skills/ml-api-rate-limit/scripts/collect_api_metrics.py \
  after.json --baseline before.json --json
```

---

## Adapting to other domains

The execution framework is identical across incident types — only the
domain-specific reasoning changes. To build a new loop-engineered skill (Spark
OOM, Kafka consumer lag, K8s CrashLoopBackOff, DB connection exhaustion, …),
copy the `ml-api-rate-limit` folder and rewrite the `loops/`, `playbooks/`, and
`scripts/` for the new domain. Classification, verification, and learning loops
stay structurally the same.
