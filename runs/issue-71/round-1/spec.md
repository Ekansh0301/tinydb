# Spec
## Source statements
S1: "For price filters I keep writing two conditions: db.search((where('price') >= 10) & (where('price') <= 20))"
S2: "It would be nicer to have db.search(where('price').between(10, 20))"
S3: "Both ends should be included."
S4: "Documents where the field is missing or None should just not match (no error)."
S5: "It should work for numbers and for strings."

## Requirements
- FR-1 [STATED] The system shall provide a `between(low, high)` method on a `Query` object returned by `where(field_name)` that builds a query matching documents whose field value is greater than or equal to `low` and less than or equal to `high`. (S2, S3)  
- FR-2 [STATED] The `between` query shall treat missing fields or fields whose value is `None` as non‑matching without raising an exception. (S4)  
- FR-3 [STATED] The `between` query shall support field values of numeric types (int, float) and string types, using the natural ordering of those types. (S5)  
- FR-4 [INFERRED] The `between` method shall return a `QueryInstance` (or subclass) that is callable with a document mapping and returns a boolean according to the semantics of FR‑1‑FR‑3. (S2)  
- FR-5 [INFERRED] The `between` query shall be hashable and compatible with TinyDB’s query‑caching mechanism. (implicit from existing Query behavior)  

## Acceptance criteria
- AC-1 (FR-1, FR-2, FR-3): Given a TinyDB instance `db` containing documents `{'price': 15}`, `{'price': 10}`, `{'price': 20}`, `{'price': 9}`, `{'price': None}`, `{}`; when executing `db.search(where('price').between(10, 20))`, then the result list shall contain exactly the three documents with `price` values 10, 15, and 20, in any order.  
- AC-2 (FR-1, FR-2, FR-3): Given a document `{'name': 'bob'}` and a query `where('name').between('alice', 'charlie')`; when the query is called with the document, then it shall return `True` because `'bob'` lies lexicographically between `'alice'` and `'charlie'`.  
- AC-3 (FR-1, FR-2, FR-3): Given a document `{'price': 25}` and the same query as AC‑1; when the query is called, then it shall return `False`.  
- AC-4 (FR-4): Given a `Query` object `q = where('price').between(5, 10)`, when `hash(q)` is computed twice, then the two hash values shall be equal.  
- AC-5 (FR-5): Given two identical `between` queries `q1 = where('price').between(5, 10)` and `q2 = where('price').between(5, 10)`, when they are used as keys in a dictionary, then `dict([ (q1, 'a'), (q2, 'b') ])` shall contain a single entry (the second insertion overwrites the first), demonstrating that they are considered equal for caching purposes.  

## Assumptions and open questions
- A-1 [ASSUMED] The `where` function returns an instance of `Query` that already supports operator overloads (`>=`, `<=`, `&`, `|`). Impact if wrong: If `where` returns a different type, the `between` method may need to be added to that type instead of `Query`. Question: Does the current TinyDB API expose `where` as a factory for `Query` objects? (Checked in `tinydb/queries.py` – it returns a `Query`.)  

## Non-goals
- Supporting open‑ended ranges (e.g., only a lower bound or only an upper bound).  
- Custom comparison functions or locale‑aware string ordering.  
- Handling of non‑orderable types (e.g., lists, dicts); such inputs are outside the scope of this feature.
