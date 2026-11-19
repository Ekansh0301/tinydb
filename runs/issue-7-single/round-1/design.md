# Design
## Approach
Add a `limit` keyword argument with default `None` to `Table.search`. Keep the existing query‑caching behavior unchanged: cache the full result list, then slice it according to `limit` before returning. Ensure the method signature is updated in the stub and docstring, and that type hints reflect the optional limit.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | Add `limit: int | None = None` parameter; after caching, slice `docs` with `docs[:limit]` when limit is not None. Update docstring accordingly. | AC-1, AC-2 |
| tests/test_autose_limit.py | new test file | Add two tests covering AC‑1 and AC‑2. | AC-1, AC-2 |

## Existing tests affected
None – existing tests exercised the original signature; they will continue to pass because the new signature is backward compatible.

## Risks
- Risk 1: Incorrect placement of the limit slice could truncate the cached list; we cache the full list (`docs[:]`) before slicing.
- Risk 2: Type hint mismatch could break static analysis but does not affect runtime.
- Risk 3: Changing the method signature may affect external code that uses positional arguments; however, `limit` is added as a keyword‑only argument after `cond`, preserving existing positional usage.
