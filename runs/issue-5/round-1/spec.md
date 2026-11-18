# Spec
## Source statements
S1: "I fetch some documents, tweak them in memory for a report, and don't call `update()`:"  
S2: ```python
users = db.search(where('team') == 'red')
users[0]['name'] = 'REDACTED'      # only for the printout
...
db.search(where('team') == 'red')[0]['name']   # -> 'REDACTED'
```  
S3: "The file on disk is untouched, but the second `search()` with the same query returns the edited name."  
S4: "If I change something nested (e.g. append to a list inside a document) the same thing happens."  
S5: "It took me a while to work out that the results come from some cache."  
S6: "I'd expect the documents I get back to be mine to modify without affecting later searches or the database."

## Requirements
- FR-1 [STATED] The system shall return document objects from `db.search()` that are independent copies of the stored data, so that modifications to the returned objects do not affect subsequent `search()` results. (S1, S2, S3, S5, S6)  
- FR-2 [STATED] The system shall not persist any changes made to document objects unless an explicit `update()` (or equivalent) call is performed. (S1, S2, S6)  
- FR-3 [INFERRED] The system would provide a configuration option to disable the caching of search result objects, ensuring a fresh copy is produced on each call. (S5)  
- FR-4 [ASSUMED] The system would expose a method or flag (e.g., `db.search(..., copy=True)`) that allows callers to request deep‑copied results on demand. Impact if wrong: If the library already returns deep copies by default, adding such a flag would be unnecessary and could confuse users. Question: Does the current API already support a deep‑copy mode?  

## Acceptance criteria
- AC-1 (FR-1): Given a database containing a document `{'team': 'red', 'name': 'Alice'}`, when `users = db.search(where('team') == 'red')` is executed, and then `users[0]['name'] = 'REDACTED'` is performed, then a subsequent call `db.search(where('team') == 'red')[0]['name']` shall return `'Alice'`.  
- AC-2 (FR-2): Given the same setup, when no `update()` call is made after modifying `users[0]`, then the on‑disk file representing the document shall remain unchanged (its contents still contain `'Alice'`).  
- AC-3 (FR-3): Given a configuration setting `cache_enabled = False`, when `db.search(where('team') == 'red')` is called twice without intervening updates, then the two returned document objects shall be distinct instances (object identity comparison is false) and modifications to the first shall not be reflected in the second.  
- AC-4 (FR-4): Given the API supports a `copy=True` argument, when `db.search(where('team') == 'red', copy=True)` is called, then the returned document objects shall be deep copies of the stored data (modifying any nested list or dict does not affect subsequent searches).  

## Assumptions and open questions
- A-1 [ASSUMED] The library currently caches whole document objects rather than query results metadata. Impact if wrong: If only query metadata is cached and objects are already copied, the proposed changes may be unnecessary. Question: Does the existing implementation reuse the same Python object instances across `search()` calls?  
- A-2 [ASSUMED] The `where` function and `db.search` API accept additional keyword arguments (e.g., `copy`). Impact if wrong: If the API is fixed and cannot be extended, the specification would need to rely solely on a global configuration flag instead of per‑call arguments. Question: Is the `search` method signature extensible?  

## Non-goals
- Changing the persistence format or location of the underlying database files.  
- Implementing a full version‑control system for document edits.  
- Providing automatic undo/redo functionality for in‑memory modifications.
