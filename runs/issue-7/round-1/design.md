# Design
## Approach
Add an optional `limit` keyword to `Table.search`. The method will validate the argument, raise a `ValueError` for non‑integer or negative values, and treat `None` as “no limit”. The full result set will still be cached, and the returned list will be sliced according to `limit` while preserving order. No other modules need changes because `TinyDB.__getattr__` forwards calls to the default `Table`, and named tables already use the same `Table.search` implementation.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Change signature to `def search(self, cond: QueryLike, limit: int | None = None) -> list[Document]`.<br>• Add validation: if `limit` is not `None` and not an `int` → raise `ValueError`; if `limit < 0` → raise `ValueError` with message “limit must be a non‑negative integer”.<br>• After building the full `docs` list, store it in the cache as before.<br>• Return `docs[:]` when `limit is None`, otherwise return `docs[:limit]`.<br>• Update docstring to describe the new argument and behaviour. | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 |
| tinydb/__init__.py | (none) | No change needed; re‑export unchanged. | — |
| tests (if any) | (none) | No test file needs modification because existing tests call `search` without `limit`. New tests for the limit behaviour will pass with the implementation above. | — |

## Existing tests affected
None. All current tests invoke `search` without a `limit` argument, which continues to behave exactly as before.

## Risks
- **Cache size impact**: caching the full result set may increase memory usage for very large tables when many limited searches are performed, but this follows the existing caching strategy.
- **Signature change**: external code that uses positional arguments expecting only `cond` will still work because `limit` is a keyword‑only argument with a default; however, code that passes a second positional argument will now receive a `TypeError`. This is acceptable given the library’s public API expectations.
