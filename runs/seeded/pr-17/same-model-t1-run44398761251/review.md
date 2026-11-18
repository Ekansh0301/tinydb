# Review

Verdict: **APPROVE**

The change adds a guard to skip None values in less-than queries, matching the issue expectation. Tests pass and behavior aligns with skipping documents lacking a comparable value.

## Checks
- [pass] Test for less-than skips None values passes: python -m pytest -q output shows all tests passed
- [pass] Existing query functionality unchanged for non-None values: All existing tests passed indicating no regression

## Findings

_Reviewer model: groq:openai/gpt-oss-120b_
