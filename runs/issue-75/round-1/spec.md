# Spec
## Source statements
S1: "I search names a lot and the regex version is awkward: db.search(where('name').matches(r'.*son.*'))"  
S2: "Could there be a plain substring check? db.search(where('name').contains_text('son'))"  
S3: "Only strings should match. Documents where the field is missing, None or a number should just not match (no error). Case-sensitive is fine."

## Requirements
- FR-1 [STATED] The system shall provide a `contains_text` operator that can be used in a query expression, e.g., `where('field').contains_text('sub')` (S2).  
- FR-2 [STATED] The `contains_text` operator shall perform a case‑sensitive substring check on the field value (S3).  
- FR-3 [STATED] When the target field is missing, has a value of `None`, or is not a string (e.g., a number), the `contains_text` operator shall evaluate to *false* for that document and must not raise an exception (S3).  
- FR-4 [INFERRED] The `contains_text` operator shall return a boolean value that can be combined with other query predicates using the existing logical operators (`and`, `or`, `not`) in the query builder (derived from the behavior of the existing `matches` operator).  
- FR-5 [INFERRED] The `contains_text` operator shall be implemented as a method of the same object returned by `where(field)` so that its usage mirrors that of the existing `matches` method (derived from the API pattern shown in S1 and S2).  

## Acceptance criteria
- AC-1 (FR-1): Given a collection containing documents `{'name': 'Jackson'}` and `{'name': 'Emily'}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall contain only the document `{'name': 'Jackson'}`.  
- AC-2 (FR-2): Given a document `{'name': 'Jackson'}`, when `db.search(where('name').contains_text('Son'))` is executed, then the result set shall be empty, confirming case‑sensitivity.  
- AC-3 (FR-3): Given a document `{'age': 30}` (field missing), when `db.search(where('name').contains_text('son'))` is executed, then the result set shall be empty and no exception shall be raised.  
- AC-4 (FR-3): Given a document `{'name': None}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall be empty and no exception shall be raised.  
- AC-5 (FR-3): Given a document `{'name': 12345}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall be empty and no exception shall be raised.  
- AC-6 (FR-4): Given three documents with names `'Jackson'`, `'Jason'`, and `'Emily'`, when `db.search(where('name').contains_text('son').and(where('age').greater_than(20)))` is executed (assuming `greater_than` exists), then the result set shall contain only `'Jackson'` and `'Jason'` if they also satisfy the age predicate, demonstrating boolean composability.  
- AC-7 (FR-5): Given the source code for the query builder, when the `where('field')` object is inspected, it shall expose a method named `contains_text` that accepts a single string argument (the substring) and returns a predicate object compatible with the query engine.  

## Assumptions and open questions
- A-1 [ASSUMED] The query engine returns a list (or iterable) of matching documents; this is the observable result used in the acceptance criteria. Impact if wrong: If the engine returns a different structure (e.g., a cursor), the test harness must adapt to inspect the returned items. Question: What exact type does `db.search` return?  
- A-2 [ASSUMED] The existing `matches` operator is case‑sensitive; the request “Case-sensitive is fine” is interpreted as requiring the same behavior for `contains_text`. Impact if wrong: If `matches` is actually case‑insensitive, the implementation may need a configurable flag. Question: What is the current case‑sensitivity of `matches`?  

## Non-goals
- Supporting case‑insensitive substring searches (not requested).  
- Providing fuzzy or approximate matching capabilities.  
- Extending `contains_text` to non‑string data types beyond the defined “no match” behavior.
