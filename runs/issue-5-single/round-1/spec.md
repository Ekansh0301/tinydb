# Spec
## Source statements
S1: Users modify returned documents from `search()` and expect later searches to return original, unmodified data. (issue description)

## Requirements
- FR-1 [STATED] The `Table.search` method shall return deep copies of cached documents so that modifications to the returned objects do not affect future query results. (S1)
- FR-2 [STATED] The per‑table query cache shall store deep copies of documents, not references to the original in‑memory documents. (S1)

## Acceptance criteria
- AC-1 (FR-1): Given a database with a document `{'team':'red','name':'Alice'}`, when `users = db.search(where('team') == 'red')` and `users[0]['name'] = 'REDACTED'`, then a subsequent `db.search(where('team') == 'red')[0]['name']` shall return `'Alice'`.
- AC-2 (FR-2): Given a database with a document `{'team':'red','tags':['a','b']}`, when `users = db.search(where('team') == 'red')` and `users[0]['tags'].append('c')`, then a subsequent `db.search(where('team') == 'red')[0]['tags']` shall return `['a','b']`.

## Assumptions and open questions
- A-1 [ASSUMED] The cache is only used for read‑only queries; writes always clear the cache, so deep‑copying cached results does not interfere with write semantics. Impact if wrong: may increase memory usage but functional correctness is preserved.

## Non-goals
- Optimising cache memory usage beyond ensuring correctness.
- Changing behaviour of non‑cacheable queries.
