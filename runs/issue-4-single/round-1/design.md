# Design
## Approach
Add a small utility `_safe_compare` that catches `TypeError` and treats `None` as non‑matching. Replace the lambda bodies of `Query.__lt__`, `__le__`, `__gt__`, and `__ge__` with calls to `_safe_compare`. This keeps the public API unchanged, preserves hash generation (hash values remain based on the operation name, path and RHS), and isolates the new behaviour to the comparison layer.

## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/queries.py | import section | Add import of `re` (already present) and define `_safe_compare` helper. | AC-1, AC-2, AC-3 |
| tinydb/queries.py | Query.__lt__ | Replace lambda with `lambda value: _safe_compare(value, rhs, lambda a,b: a < b)` | AC-1 |
| tinydb/queries.py | Query.__le__ | Replace lambda with `lambda value: _safe_compare(value, rhs, lambda a,b: a <= b)` | AC-1 |
| tinydb/queries.py | Query.__gt__ | Replace lambda with `lambda value: _safe_compare(value, rhs, lambda a,b: a > b)` | AC-2 |
| tinydb/queries.py | Query.__ge__ | Replace lambda with `lambda value: _safe_compare(value, rhs, lambda a,b: a >= b)` | AC-2, AC-3 |

## Existing tests affected
None directly; existing tests expecting a `TypeError` will be updated implicitly by the new behaviour. No existing test relies on the exception being raised.

## Risks
- Risk 1: Cache hash values may become non‑deterministic if the lambda now closes over the helper; however the hash generation uses a static tuple (`('<', self._path, rhs)`) unchanged, so cache behaviour is preserved.  
- Risk 2: The new helper could mask genuine programming errors where a comparison should be allowed but fails for another reason; acceptable given the library’s philosophy of forgiving queries.  
- Risk 3: If other modules import `Query.__lt__` directly (unlikely), their semantics change; but this is the intended change.
