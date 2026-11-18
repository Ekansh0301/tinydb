# Design
## Approach
We will extend the query language by adding two new methods, `startswith` and `endswith`, to the `Query` class in `tinydb/queries.py`. Both will follow the same pattern as the existing `matches` method: they will generate a test callable that first checks that the examined value is a string, then applies the appropriate string method, and finally produce a deterministic hash tuple that includes the operation name, the field path, and the supplied argument. This satisfies FR‑1‑FR‑4 while preserving the query‑caching contract (C4). No other files need to be touched, and existing behaviour (including the `matches` operator) remains unchanged.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/queries.py | `Query` | **NEW** method `def startswith(self, prefix: str) -> QueryInstance:` – creates a test that returns `False` for non‑strings, otherwise `value.startswith(prefix)`. Hash value: `('startswith', self._path, prefix)`. | AC‑1, AC‑3, AC‑5 |
| tinydb/queries.py | `Query` | **NEW** method `def endswith(self, suffix: str) -> QueryInstance:` – creates a test that returns `False` for non‑strings, otherwise `value.endswith(suffix)`. Hash value: `('endswith', self._path, suffix)`. | AC‑2, AC‑4 |
| tinydb/queries.py | `Query` | Insert the two new methods after the existing `matches` implementation (maintaining code order). | – |

## Existing tests affected
none – there are currently no tests exercising `startswith`/`endswith`; adding these methods does not alter existing query behaviour.

## Risks
- If future code relies on `Query`’s `__dir__` or similar introspection, the added methods could appear unexpectedly, but this is harmless for current usage.  
- Incorrect hash construction could break cache identity; the plan mirrors the pattern used by `matches`, minimizing that risk.
