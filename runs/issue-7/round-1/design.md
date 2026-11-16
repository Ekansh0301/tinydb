# Design
## Approach
The `Table.search` method is the single entry point for all query executions, including calls via `TinyDB.__getattr__`. By extending its signature with an optional keyword‑only `limit` argument we can satisfy the new functional requirements without touching any other component. The existing cache will continue to store the full result set; the limit is applied only to the returned slice, preserving cache correctness. Input validation will coerce non‑positive limits to an empty list, and limits larger than the result size will simply return the full list, matching the specified behaviour.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Add a keyword‑only parameter `limit: int | None = None`.<br>• Update docstring to describe the new argument and its semantics.<br>• When a cached result is used, return `cached_results[:limit]` if `limit` is not `None` (handling `limit <= 0` → empty list).<br>• After computing `docs`, store the full list in the cache as before, then apply the same slicing logic before returning.<br>• Raise `TypeError` only if `limit` is provided but not an `int`. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5, AC‑6 |

## Existing tests affected
none – the existing test suite only exercises the original un‑limited behaviour, which remains unchanged when `limit` is omitted.

## Risks
- Adding a keyword‑only argument could break user code that previously passed a positional argument after `cond`; however, all current usages in the library call `search` with a single positional argument, so compatibility is maintained.
- Slicing the cached list on each call adds negligible overhead but must not mutate the cached data; the implementation uses `cached_results[:limit]` which returns a new list, preserving cache integrity.


## Stopped
Stage 2 could not pass its check: agent stopped: model unavailable: all tiers failed: groq:openai/gpt-oss-120b HTTP 429 {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01knz0bvj3f2wbzwfq04phs5md` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 198307, Requested 3721. Please try again in 14m36.096s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing","type":"tokens","code":"rate_limit_exceeded"}}

