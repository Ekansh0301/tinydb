# Spec
## Source statements
S1: "For price filters I keep writing two conditions: db.search((where('price') >= 10) & (where('price') <= 20))"  
S2: "It would be nicer to have db.search(where('price').between(10, 20))"  
S3: "Both ends should be included."  
S4: "Documents where the field is missing or None should just not match (no error)."  
S5: "It should work for numbers and for strings."

## Requirements
- FR-1 [STATED] The system shall provide a `between(low, high)` method on the object returned by `where(field_name)` that can be used inside `db.search(...)` (S2).  
- FR-2 [STATED] The `between` method shall treat the lower and upper bounds as inclusive, i.e., a document whose field value equals `low` or `high` shall match (S3).  
- FR-3 [STATED] When a document does not contain the queried field or the field value is `None`, the `between` predicate shall evaluate to *false* without raising an exception (S4).  
- FR-4 [STATED] The `between` method shall operate correctly for fields whose values are numbers (int, float) and for fields whose values are strings, using the natural ordering of the respective type (S5).  
- FR-5 [INFERRED] The `between` predicate shall be combinable with other predicates using logical operators (`&`, `|`, `~`) in the same way as existing comparison predicates (S1, S2).  

## Acceptance criteria
- AC-1 (FR-1): Given a collection with a document `{'price': 15}`, when `db.search(where('price').between(10, 20))` is executed, then the result set contains that document.  
- AC-2 (FR-2): Given a document `{'price': 10}` and another `{'price': 20}`, when `db.search(where('price').between(10, 20))` is executed, then both documents are present in the result set.  
- AC-3 (FR-3): Given a document `{'name': 'Alice'}` (no `price` field) and a document `{'price': None}`, when `db.search(where('price').between(5, 15))` is executed, then neither document appears in the result set and no exception is raised.  
- AC-4 (FR-4 – numbers): Given a document `{'age': 30}`, when `db.search(where('age').between(25, 35))` is executed, then the document is returned.  
- AC-5 (FR-4 – strings): Given a document `{'code': 'B'}`, when `db.search(where('code').between('A', 'C'))` is executed, then the document is returned.  
- AC-6 (FR-5): Given documents `{'price': 12}`, `{'price': 18}`, and `{'price': 25}`, when `db.search(where('price').between(10, 20) & (where('price') != 18))` is executed, then only the document with `price` 12 is returned.  

## Assumptions and open questions
- A-1 [ASSUMED] The underlying storage engine supports ordering comparisons for string values in the same lexical order as Python's default string comparison. Impact if wrong: `between` on strings could yield unexpected matches; the test suite would need to verify ordering semantics. Question: Does the database treat strings case‑sensitively and does it use Unicode code‑point order?  
- A-2 [ASSUMED] The `where` function returns an object that can be extended with additional methods without breaking existing API contracts. Impact if wrong: Adding `between` could cause method‑resolution conflicts; integration tests would reveal any breakage.  

## Non-goals
- Support for open (exclusive) interval bounds.  
- Automatic type coercion between numbers and strings.  
- Handling of complex nested fields (e.g., `where('address.city')`).
