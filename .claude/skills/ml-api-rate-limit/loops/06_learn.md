# Loop 6: Learning

## Goal
Convert the resolved incident into reusable, structured knowledge so the next
incident starts smarter than this one.

## Input
The full trail: classification, evidence, diagnosis, mitigation, verification.

## Actions
1. Record the incident as a structured record (below).
2. Update the matching `playbooks/*.md` if a new signal or fix was learned.
3. Append the case to `evals/golden_429_cases.json` as a regression test.
4. Draft a knowledge base article from the record.
5. Adjust confidence heuristics used in Diagnosis if the ranking was wrong.

## Structured Record

```json
{
  "incident": "",
  "root_cause": "",
  "successful_mitigation": "",
  "sdk_version": "",
  "verification": "",
  "confidence": 0,
  "playbook_updates": [],
  "kb_article_title": ""
}
```

## Output
A short summary of what was learned and which artifacts were updated.
