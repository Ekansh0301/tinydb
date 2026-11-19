# Design
## Approach
Modify the internal lambda used for the four range operators to first check that the document value is comparable to the RHS. The safest way is to attempt the comparison inside a `try/except TypeError` block and return `False` on failure, which makes the document be filtered out. Implement a small helper `_safe_compare` to keep the code tidy and reuse it for `<`, `<=`, `>`, `>=`. Keep the hash generation unchanged (the RHS is still part of the hash) so caching behaviour is unaffected.

## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/queries.py | `Query.__lt__`, `__le__`, `__gt__`, `__ge__` | Replace the lambda with one that calls `_safe_compare` (which catches `TypeError` and returns `False`). Add `_safe_compare` helper at top of file. | AC-1, AC-2, AC-3, AC-4 |

## Existing tests affected
None (new behaviour only adds safety; existing equality/inequality tests continue to pass).

## Risks
- May affect query caching if the hash value changes; we keep the hash tuple unchanged, so cache keys remain identical.
- Introducing a helper function must not create circular imports; it lives in the same module and only uses built‑ins.
- The broader “skip on TypeError” rule could hide programmer errors, but it matches the documented expectation for range queries.
