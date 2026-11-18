# Review

Verdict: **APPROVE**

The change adds a guard to skip None values in less-than queries, matching the issue expectation. Tests pass and existing behavior is unchanged.

## Checks
- [pass] None values are skipped in '<' queries: test_less_than_skips_none passed
- [pass] All tests pass after change: pytest exit code 0 with all tests passing

## Findings

_Reviewer model: groq:openai/gpt-oss-120b_
