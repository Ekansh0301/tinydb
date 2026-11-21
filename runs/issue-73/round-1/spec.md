# Spec
## Source statements
S1: "I search names a lot and the regex version is awkward: db.search(where('name').matches(r'.*son.*'))"  
S2: "Could there be a plain substring check? db.search(where('name').contains_text('son'))"  
S3: "Only strings should match."  
S4: "Documents where the field is missing, None or a number should just not match (no error)."  
S5: "Case-sensitive is fine."

## Requirements
- FR-1 [STATED] The system shall provide a `contains_text(substring)` operator that can be used in a `where` clause, e.g., `where('name').contains_text('son')`. (S2)  
- FR-2 [STATED] The `contains_text` operator shall perform a case‑sensitive substring search. (S5)  
- FR-3 [INFERRED] The `contains_text` operator shall return a match only when the target field’s value is a string that contains the supplied substring. (S3, S4)  
- FR-4 [STATED] When the target field is missing, has a value of `None`, or is not a string (e.g., a number), the document shall be treated as non‑matching and no exception shall be raised. (S4)

## Acceptance criteria
- AC-1 (FR-1, FR-2, FR-3): Given a collection containing a document `{'name': 'Jackson'}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall include that document.  
- AC-2 (FR-1, FR-2, FR-3): Given a collection containing a document `{'name': 'Jackson'}`, when `db.search(where('name').contains_text('Son'))` is executed, then the result set shall **not** include that document (case‑sensitive).  
- AC-3 (FR-4): Given a collection containing a document `{'age': 30}` (field missing), when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.  
- AC-4 (FR-4): Given a collection containing a document `{'name': None}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.  
- AC-5 (FR-4): Given a collection containing a document `{'name': 12345}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.  

## Assumptions and open questions
- A-1 [ASSUMED] The underlying query engine can be extended with a new operator without breaking existing operators. Impact if wrong: adding `contains_text` could require changes to the query parser or execution engine, potentially affecting performance or compatibility with existing queries. Question: Does the current query implementation expose a registration mechanism for custom operators?  

## Non-goals
- Implementing case‑insensitive or regex‑based substring searches (the request explicitly states case‑sensitive is fine).  
- Providing locale‑aware or Unicode normalization handling for substring matching.  
- Changing the behavior of existing `matches` operator.
