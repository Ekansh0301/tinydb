# Spec
## Source statements
S1: Users may store `None` in a document field (e.g., `price`).  
S2: Range queries using `<`, `>`, `<=`, `>=` raise `TypeError` when a field contains `None`.  
S3: Existing behaviour already skips documents that completely lack the field.  
S4: Desired behaviour: range queries should skip documents where the field value is `None` (or of an incomparable type) rather than raising an error.  

## Requirements
- FR-1 [STATED] The query operators `<`, `>`, `<=`, `>=` shall return `False` for a document when the field value is `None` (S2, S4).  
- FR-2 [INFERRED] The query operators shall also return `False` when the field value is of a type that cannot be compared with the right‑hand side (e.g., mixing strings and numbers) (S4).  
- FR-3 [ASSUMED] The change must not affect the existing semantics for comparable values (i.e., `value < rhs` should still be true when both are comparable) (impact if wrong: existing tests would fail).

## Acceptance criteria
- AC-1 (FR-1): Given a table containing documents `{'price': None}` and `{'price': 10}`, when executing `db.search(where('price') < 20)`, then the result list contains only the document with price 10 and no exception is raised.  
- AC-2 (FR-2): Given a table containing documents `{'price': 'free'}` and `{'price': 5}`, when executing `db.search(where('price') > 2)`, then the result list contains only the document with price 5 and no exception is raised.  
- AC-3 (FR-3): Given a table containing documents `{'price': 15}` and `{'price': 5}`, when executing `db.search(where('price') >= 10)`, then the result list contains only the document with price 15.  

## Assumptions and open questions
- A-1 [ASSUMED] Introducing a helper `_safe_compare` in `tinydb/queries.py` does not conflict with any existing imports or name resolution. Impact if wrong: import errors.  
- A-2 [ASSUMED] Changing only the lambda functions for the four comparison methods is sufficient; no other parts (e.g., hash generation) need adjustment. Impact if wrong: cache identity may become inconsistent, causing stale cache results.  

## Non-goals
- Changing the behaviour of equality/inequality operators.  
- Providing user‑configurable comparison policies.  
- Modifying storage or other components.
