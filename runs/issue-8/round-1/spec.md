# Spec
## Source statements
S1: "I called remove with a query and a list of ids at the same time because I wanted to be safe, and a document that has nothing to do with my query is gone."  
S2: "Same with update, it changed a document I didn't expect."  
S3: "Pretty sure this didn't used to happen."

## Requirements
- FR-1 [STATED] The system shall remove a document only when **both** the supplied query (`cond`) matches the document **and** the document’s ID is included in the supplied `doc_ids` list (S1).  
- FR-2 [STATED] The system shall update a document only when **both** the supplied query (`cond`) matches the document **and** the document’s ID is included in the supplied `doc_ids` list (S2).  
- FR-3 [INFERRED] The system would treat the combination of `cond` and `doc_ids` as an atomic operation: the set of documents evaluated is the intersection of the query result set and the explicit ID list, and the operation either succeeds for all intersecting documents or fails without partial changes (see atomicity comment in `tinydb/table.py` lines 651‑658) (FR-1, FR-2).  
- FR-4 [ASSUMED] The system would raise a `ValueError` if neither a query nor a `doc_ids` list is provided, preserving the existing validation behaviour (see `tinydb/table.py` lines 607‑610) (no direct statement in the issue).  
- FR-5 [ASSUMED] The system would return a list of IDs of the documents that were actually removed or updated, excluding any IDs that did not correspond to existing documents (see documentation in `tinydb/table.py` lines 633‑639) (no direct statement in the issue).

## Acceptance criteria
- AC-1 (FR-1): Given a table containing documents with IDs 1, 2, 3 where document 2 matches the query `where('type') == 'target'`, when `table.remove(where('type') == 'target', doc_ids=[1,2,3])` is called, then the returned list is `[2]` and only document 2 is removed; documents 1 and 3 remain.  
- AC-2 (FR-2): Given a table containing documents with IDs 4, 5, 6 where document 5 matches the query `where('status') == 'old'`, when `table.update({'status': 'new'}, where('status') == 'old', doc_ids=[4,5,6])` is called, then the returned list is `[5]` and only document 5 is updated; documents 4 and 6 remain unchanged.  
- AC-3 (FR-3): Given a table where documents 7 and 8 both satisfy the query `where('flag') == True`, when `table.remove(where('flag') == True, doc_ids=[7,8])` is called, then both documents are removed and the returned list is `[7,8]`; if an exception occurs during removal, the table state after the call is identical to the state before the call.  
- AC-4 (FR-4): Given an empty table, when `table.remove()` is called with no arguments, then a `ValueError` is raised with a message containing “must specify a doc_id”.  
- AC-5 (FR-5): Given a table containing documents with IDs 9 and 10, when `table.remove(doc_ids=[9,99])` is called, then the returned list is `[9]` and document 9 is removed while document 10 remains; ID 99 is silently ignored.

## Assumptions and open questions
- A-1 [ASSUMED] The current implementation of `remove` and `update` already treats `doc_ids` and `cond` independently (i.e., it applies the query *or* the ID list). Impact if wrong: the specification would conflict with existing behaviour, requiring a code change that could break downstream code relying on the old semantics. Question: Does the library historically treat both parameters as a logical **AND**, or has it always been **OR**?  
- A-2 [ASSUMED] The atomicity comment in `tinydb/table.py` (lines 651‑658) applies equally to `update` as it does to `remove`. Impact if wrong: the acceptance criterion AC‑3 may be invalid for `update`; a separate atomicity guarantee might be needed. Question: Is `update` implemented with the same internal `updater` pattern guaranteeing atomicity?  

## Non-goals
- Changing the public API (e.g., renaming parameters) is out of scope.  
- Performance optimisations beyond ensuring correct logical combination are out of scope.  
- Compatibility with legacy code that relied on the previous (potentially incorrect) behaviour is not addressed; migration guidance is outside this specification.
