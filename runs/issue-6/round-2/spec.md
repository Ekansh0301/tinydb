# Spec
## Source statements
S1: "For name lookups I keep writing regexes: `db.search(where('name').matches(r'^Al'))`"  
S2: "It would be nicer to have `db.search(where('name').startswith('Al'))` `db.search(where('name').endswith('son'))`"  
S3: "Only strings should match; documents where the field is missing, `None` or a number should just not match (no error). Case-sensitive is fine."

## Requirements
- FR-1 [STATED] The system shall provide a `startswith` operator that can be used as `where('<field>').startswith('<prefix>')` in a query. (S2)  
- FR-2 [STATED] The system shall provide an `endswith` operator that can be used as `where('<field>').endswith('<suffix>')` in a query. (S2)  
- FR-3 [STATED] The `startswith` and `endswith` operators shall match only documents whose target field value is a string; documents where the field is missing, `None`, or a non‑string (e.g., number) shall not be returned and shall not raise an exception. (S3)  
- FR-4 [STATED] Matching performed by `startswith` and `endswith` shall be case‑sensitive. (S3)  

## Acceptance criteria
- AC-1 (FR-1): Given a collection containing documents `{'name': 'Alice'}` and `{'name': 'Bob'}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}`.  
- AC-2 (FR-2): Given a collection containing documents `{'name': 'Jackson'}` and `{'name': 'John'}`, when `db.search(where('name').endswith('son'))` is executed, then the result set shall contain only the document `{'name': 'Jackson'}`.  
- AC-3 (FR-3): Given a collection containing documents `{'name': 'Alice'}`, `{}` (field missing), `{'name': None}`, and `{'name': 123}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}` and no exception shall be raised.  
- AC-4 (FR-3): Given a collection containing documents `{'name': 'Alice'}`, `{}` (field missing), `{'name': None}`, and `{'name': 123}`, when `db.search(where('name').endswith('ice'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}` and no exception shall be raised.  
- AC-5 (FR-4): Given a collection containing documents `{'name': 'alice'}` and `{'name': 'Alice'}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only `{'name': 'Alice'}` (case‑sensitive match).  

## Assumptions and open questions
- A-1 [ASSUMED] The underlying query engine can translate `startswith` and `endswith` into appropriate filter logic (e.g., regex `^prefix` and `suffix$`). Impact if wrong: additional implementation work may be required to add custom filter handling.  
- A-2 [ASSUMED] No existing `startswith`/`endswith` methods conflict with other parts of the API. Impact if wrong: naming collision could require alternative method names.  

## Non-goals
- Providing case‑insensitive variants of `startswith` or `endswith`.  
- Adding support for pattern matching beyond simple prefix/suffix (e.g., wildcard or regex).  
- Modifying behavior of existing `matches` operator.
