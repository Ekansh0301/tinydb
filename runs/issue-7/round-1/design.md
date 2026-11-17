# Design
## Approach
We will extend `Table.search` to accept an optional keyword argument `limit`. The existing signature will be kept backward‑compatible by giving `limit` a default value of `None`. When `limit` is provided we validate it as an integer ≥ 1, then return at most that many matching documents without caching the limited result (the cache must remain keyed only by the query). When `limit` is omitted the current behaviour – full caching and returning all matches – stays unchanged. Because `TinyDB` forwards unknown attributes to the default `Table`, the new argument automatically works for the default table and for any named table returned by `TinyDB.table(name)`.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | • Change signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`.<br>• Add validation: if `limit` is not `None` and (`not isinstance(limit, int)` or `limit < 1`) raise `TypeError`.<br>• After building the full `docs` list, if `limit` is provided return `docs[:limit]` **without** storing in the query cache.<br>• If `limit` is `None`, keep existing caching logic unchanged.<br>• Update docstring to describe the new parameter. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5 |

## Existing tests affected
None. All current tests call `search` without a `limit` argument, and the default `None` preserves existing behaviour.

## Risks
- Introducing a new positional‑only parameter could break user code that called `search` with a positional argument after the query; using a keyword‑only parameter (`*, limit`) mitigates this.
- Incorrect validation may raise the wrong exception type; we explicitly raise `TypeError` as required by FR‑1.
- Bypassing the cache for limited results could increase memory usage for repeated limited queries, but this follows the specification and does not affect existing functionality.
