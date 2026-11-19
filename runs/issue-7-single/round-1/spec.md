# Spec
## Source statements
S1: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored? Without `limit` nothing should change. It should work on named tables too."

## Requirements
- FR-1 [STATED] The `Table.search` method shall accept an optional `limit` keyword argument of type `int` or `None`. (S1)
- FR-2 [STATED] When `limit` is provided and is a positive integer, `search()` shall return at most `limit` matching documents, preserving the order in which they are stored in the table. (S1)
- FR-3 [STATED] When `limit` is omitted or `None`, `search()` shall return all matching documents, preserving existing behaviour. (S1)

## Acceptance criteria
- AC-1 (FR-1): Given a `Table` instance, when calling `table.search(cond, limit=5)`, then the method signature accepts the `limit` argument without raising a `TypeError`.
- AC-2 (FR-2): Given a table containing at least 20 documents where 15 match `cond`, when calling `table.search(cond, limit=10)`, then the returned list length is 10 and the first 10 matching documents are returned in the same order as they appear in the table.
- AC-3 (FR-3): Given a table with matching documents, when calling `table.search(cond)` (no limit) or `table.search(cond, limit=None)`, then the returned list contains all matching documents, identical to the pre‑change behaviour.

## Assumptions and open questions
- A-1 [ASSUMED] The order of documents is the iteration order of the underlying table dict (insertion order). Impact if wrong: limit would return a different subset than expected.
- A-2 [ASSUMED] The existing query cache stores the full result list; limiting should be applied **after** retrieving (and possibly caching) the full list to keep cache semantics unchanged. Impact if wrong: cached results could be truncated incorrectly.

## Non-goals
- Adding support for offset/skip functionality.
- Changing the underlying storage format or query cache semantics beyond what is needed for limiting.
