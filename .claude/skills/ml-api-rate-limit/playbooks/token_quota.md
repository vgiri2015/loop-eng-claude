# Playbook: Token-Per-Minute Limit Exceeded

## Summary
Request *count* is within limits, but total input+output **tokens per minute**
exceed the account's TPM quota. Large prompts, long contexts, or high
`max_tokens` consume the budget faster than the request rate suggests.

## Confirming Signals
- Error/body mentions tokens or TPM, not request count.
- Token usage per minute is at or above the account TPM limit.
- Request rate is comfortably under the RPM limit while 429s still occur.
- Large average prompt size, long contexts, or high `max_tokens`.
- Streaming calls hold token budget for the full generation window.

## Refuting Signals
- Request rate is the binding constraint, tokens are low → [[burst_quota]].
- 429s grow with retries → [[retry_storm]].
- Isolated to one region → [[regional_throttling]].

## Immediate Mitigation
- Lower `max_tokens` to the smallest value that satisfies the use case.
- Trim prompt/context size; drop redundant history.
- Reduce concurrency of token-heavy calls so they don't stack within a minute.
- Respect `Retry-After` and back off on token-limit 429s.

## Long-Term Remediation
- Budget tokens per minute client-side (token-aware rate limiter, not just RPM).
- Cache or summarize long contexts; use smaller models where adequate.
- Request a TPM increase if the workload legitimately needs it.

## Verification
- Tokens-per-minute stays under the TPM ceiling.
- 429s citing token limits stop recurring.
