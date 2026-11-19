# Spec
## Source statements
S1: "remove() deleted the wrong thing ... I called remove with a query and a list of ids at the same time ... a document that has nothing to do with my query is gone."
## Requirements
- FR-1 [STATED] The `Table.remove` method shall, when both `doc_ids` and `cond` are provided, remove only documents whose ID is in `doc_ids` **and** that satisfy the condition. (S1)
- FR-2 [STATED] When only `doc_ids` is provided, `Table.remove` shall remove the documents with those IDs, unchanged from previous behaviour. (S1)
- FR-3 [STATED] When only `cond` is provided, `Table.remove` shall remove all documents matching the condition, unchanged from previous behaviour. (S1)
## Acceptance criteria
- AC-1 (FR-1): Given a table with documents of differing types, when `remove(doc_ids=[id1,id2], cond=Query().type == 'a')` is called, then only the document whose ID is in the list **and** whose `type` equals `'a'` is removed, and the returned list contains exactly that ID.
- AC-2 (FR-2): Given a table with documents, when `remove(doc_ids=[id1,id2])` is called, then both IDs are removed and the returned list contains exactly those IDs.
- AC-3 (FR-3): Given a table with documents, when `remove(cond=Query().type == 'a')` is called, then all matching documents are removed and the returned list contains their IDs.
## Assumptions and open questions
- A-1 [ASSUMED] `cond` is a `QueryInstance` that can be called as `cond(document)`. Impact if wrong: the implementation would raise a TypeError; tests would catch this.
- A-2 [ASSUMED] Document IDs are stored as integers; the method returns a list of those integers. Impact if wrong: type mismatch in tests.
## Non-goals
- Changing behaviour of other Table methods.
- Introducing new public API.
