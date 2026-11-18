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
- FR-2 [STATED] The system shall not persist any modifications made to returned document objects unless an explicit `update()` (or equivalent) call is performed. (S1, S2, S3, S6)  
- FR-3 [INFERRED] The system would provide a mechanism (e.g., a deep‑copy flag or configuration option) to control whether `search()` returns cached mutable references or fresh copies. (S5, S6)  
- FR-4 [ASSUMED] The system would expose a method or property to clear or bypass the internal cache used by `search()`. Impact if wrong: If the cache cannot be cleared, users cannot guarantee isolation of read‑only operations. Question: Does the current API expose any cache‑control functionality?  

## Acceptance criteria
- AC-1 (FR-1): Given a document stored in the database with `name = "Alice"`, when `result1 = db.search(where('team') == 'red')` and `result1[0]['name'] = 'REDACTED'`, then a subsequent call `result2 = db.search(where('team') == 'red')` shall return `result2[0]['name'] == "Alice"`.  
- AC-2 (FR-2): Given a document stored with `age = 30`, when `doc = db.search(where('id') == 42)[0]` and `doc['age'] = 99` without calling `update()`, then after the program terminates the persisted file on disk shall still contain `age = 30`.  
- AC-3 (FR-3): Given the system configured to return cached references, when the configuration is switched to “return copies”, then after performing the same modification steps as in AC-1, the second `search()` shall return the original unmodified value.  
- AC-4 (FR-4): Given a populated cache, when the user invokes the cache‑clear operation (if any), then a subsequent `search()` shall behave as if no prior `search()` had been executed, returning fresh copies of documents.  

## Assumptions and open questions
- A-1 [ASSUMED] The database library currently caches query results in memory and returns the same mutable objects on repeated queries. Impact if wrong: If no caching exists, the observed behavior must be due to another mechanism (e.g., reference sharing at a lower layer). Question: What internal data structures does `db.search()` use to store query results?  
- A-2 [ASSUMED] The library provides an `update()` method that persists changes; no other implicit persistence occurs. Impact if wrong: If there are auto‑write hooks, the requirement to avoid persistence without `update()` would be invalid. Question: Does the library have any auto‑commit or write‑through behavior?  

## Non-goals
- Changing the query language or the semantics of `where()` clauses.  
- Implementing a full version‑control system for the underlying file storage.  
- Providing UI components for editing documents; the focus is solely on the data‑access layer behavior.
