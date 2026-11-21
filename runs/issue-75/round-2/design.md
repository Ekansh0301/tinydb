# Design
## Approach
We will extend the `Query` class with a new `contains_text` method that performs a case‑sensitive substring check. The implementation mirrors the existing `matches` and `search` methods: it first verifies the document field is a string, returns `False` for missing, `None`, or non‑string values, and then uses Python’s `in` operator for the substring test. The method will generate a query hash that includes the operation name, the field path, and the substring argument so that the query cache remains correct. No other parts of the codebase need modification, and the change respects all architecture constraints.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| `tinydb/queries.py` | `class Query` | **NEW method** `def contains_text(self, substring: str) -> QueryInstance:` implementing the substring check and returning `self._generate_test(test, ('contains_text', self._path, substring))`. | AC-1, AC-2, AC-3, AC-4, AC-5 |
| `tinydb/__init__.py` | Re‑export (optional) | No change needed; `where` already returns a `Query` instance, so the new method is automatically available. | AC-1‑5 |

## Existing tests affected
none – all existing tests continue to pass; the new method adds functionality without altering existing behaviour.

## Risks
- **Cache identity:** The hash tuple must include the substring argument; forgetting it could cause cache collisions. The implementation follows the pattern used by `matches` and `search`, mitigating this risk.  
- **Future API expectations:** If downstream code expects `contains_text` to be a class method rather than an instance method, they will still receive it via the `Query` object returned by `where`, matching current usage patterns.  
- **Performance:** Using Python’s `in` operator is O(n) on the string length, which is acceptable for TinyDB’s intended small‑scale use.
