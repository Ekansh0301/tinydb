# Design
## Approach
The range‑query operators are implemented in `tinydb/queries.py` as simple lambdas that directly perform `<`, `<=`, `>`, `>=`. When a document contains `None` or a value of an incompatible type (e.g., a string versus a numeric rhs) these lambdas raise `TypeError`, breaking the whole query. We will wrap each comparison in a `try/except` block that returns `False` on any exception, which makes the document be treated as non‑existent for that query, matching the required behaviour. The hash‑generation part of the query stays unchanged, preserving caching semantics. No other module is touched, keeping the change minimal and respecting all architectural constraints.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/queries.py | `Query.__lt__` | Replace the lambda `lambda value: value < rhs` with `lambda value: _safe_compare(value, rhs, lambda a, b: a < b)` (new helper defined in the same file). | AC-1 |
| tinydb/queries.py | `Query.__le__` | Same replacement using `< =` comparator. | AC-1 |
| tinydb/queries.py | `Query.__gt__` | Same replacement using `>` comparator. | AC-2 |
| tinydb/queries.py | `Query.__ge__` | Same replacement using `>=` comparator. | AC-2 |
| tinydb/queries.py | (new) `_safe_compare` helper | Add a small private function that executes the provided comparator inside a `try/except TypeError` and returns `False` on exception. | AC-1, AC-2, AC-3, AC-4 |

## Existing tests affected
None – existing tests use comparable values and the new helper preserves correct results while only suppressing `TypeError` for incompatible values.

## Risks
- The `try/except` may mask unexpected `TypeError` sources inside user‑provided comparator logic, but the comparator is a simple built‑in operator, so this risk is minimal.  
- Adding a helper function introduces a new name in the module namespace; it is prefixed with an underscore to signal internal use and avoid public API changes.
