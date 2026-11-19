# Spec
## Source statements
S1: "Editing a document I got from search() changes what the next search returns"
S2: "I fetch some documents, tweak them in memory for a report, and don't call `update()`"
S3: "The file on disk is untouched, but the second `search()` with the same query returns the edited name."
S4: "If I change something nested (e.g. append to a list inside a document) the same thing happens."
S5: "I'd expect the documents I get back to be mine to modify without affecting later searches or the database."
## Requirements
- FR-1 [STATED] The `Table.search` method shall return fresh `Document` objects that are independent of the cached query results, so that in‑memory modifications do not affect subsequent searches. (S1, S2, S3, S4, S5)
## Acceptance criteria
- AC-1 (FR-1): Given a database with two documents matching `where('team') == 'red'`, when the first `search` result is modified (`['name'] = 'REDACTED'`), then a subsequent `search` with the same query returns the original name (`'Alice'`) and does not contain `'REDACTED'`.
- AC-2 (FR-1): Given a document with a mutable list field, when the list is mutated in a `search` result (e.g., `append('new')`), then a subsequent `search` with the same query returns the original list without the appended element.
## Assumptions and open questions
- A-1 [ASSUMED] The query cache stores the exact `Document` instances returned by a previous `search`. Impact if wrong: the fix must replace those cached objects with immutable copies or recreate fresh objects on each cache hit.
- A-2 [ASSUMED] The `Table.document_class` default is `Document` and its constructor signature is `(value: Mapping, doc_id: int)`. Impact if wrong: the fix must use the class's constructor accordingly.
## Non-goals
- Changing the caching strategy beyond returning fresh objects.
- Adding deep‑copy overhead for non‑cached queries.
