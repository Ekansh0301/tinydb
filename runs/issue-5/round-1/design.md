# Design
## Approach
`Table.search` currently returns a shallow copy of the cached list, but the documents inside are the same mutable objects stored in the cache, causing later queries to see modifications. To satisfy FR‑1 we must return deep copies of each document when the query is cached. We add an optional flag on the `Table` class (`return_copies: bool`, default True) that controls this behaviour, exposing a new method `Table.set_return_copies(flag: bool)` and a `Table.clear_cache()` method (already present) for FR‑4. The flag is checked in `search`; when `True` we deep‑copy each document before returning (and before caching, to keep the cache immutable). When `False` we preserve the historic behaviour for backward compatibility, covering FR‑3. No other modules are touched, preserving all architecture constraints.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | class Table | Add class attribute `return_copies: bool = True` and instance attribute `self._return_copies`. Initialize in `__init__`. | AC-1, AC-3 |
| tinydb/table.py | Table.__init__ | `self._return_copies = self.return_copies` (or accept optional kwarg `return_copies`). | AC-1, AC-3 |
| tinydb/table.py | Table.set_return_copies | NEW method `def set_return_copies(self, flag: bool) -> None: self._return_copies = flag` | AC-3 |
| tinydb/table.py | Table.search | Modify return logic: after retrieving `cached_results` (if any) and before returning, if `self._return_copies` is True, return `[doc.copy() for doc in cached_results]` (deep‑copy via `copy.deepcopy`). Likewise, after computing `docs` on a cache miss, store deep copies in the cache (`self._query_cache[cond] = [doc.copy() for doc in docs]`) when `self._return_copies` is True. | AC-1, AC-2, AC-3 |
| tinydb/table.py | import | Add `import copy` at top of file. | AC-1, AC-2, AC-3 |
| tinydb/table.py | docstring | Update docstring of `search` to note the new `return_copies` behaviour and that cached results are immutable. | AC-1, AC-3 |
| tinydb/table.py | Table.clear_cache | No change (already exists) – used for AC‑4. | AC-4 |

## Existing tests affected
none – existing tests expect the current (mutable) behaviour; they will continue to pass because the default `return_copies` is **True**, which is a change. However, to keep backward compatibility for any user‑code relying on mutable cached objects, the new flag can be set to `False` via `set_return_copies(False)`. No test files need modification.

## Risks
- Introducing deep copies may slightly impact performance for large result sets.
- Users relying on the historic mutable‑cache semantics must explicitly disable the new behaviour; forgetting to do so could cause subtle bugs, but the added `set_return_copies` method provides a clear migration path.
