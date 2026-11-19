# Spec
## Source statements
S1: Users want `where('name').startswith('Al')` and `where('name').endswith('son')` query helpers.
S2: Only strings should match; missing fields, `None`, or non‑string values must simply not match (no exception). Case‑sensitive matching is acceptable.

## Requirements
- FR-1 [STATED] The Query API shall provide a `startswith(prefix: str)` method that returns a `QueryInstance` matching documents whose specified field is a string starting with `prefix`. (S1)
- FR-2 [STATED] The Query API shall provide an `endswith(suffix: str)` method that returns a `QueryInstance` matching documents whose specified field is a string ending with `suffix`. (S1)
- FR-3 [STATED] For both methods, if the field is missing, `None`, or not a string, the document shall not match and no error shall be raised. (S2)

## Acceptance criteria
- AC-1 (FR-1): Given a Query built with `where('name').startswith('Al')`, when evaluating a document `{'name': 'Alice'}`, then the result is `True`.
- AC-2 (FR-1): Given the same query, when evaluating a document `{'name': 'Bob'}`, then the result is `False`.
- AC-3 (FR-1): Given the same query, when evaluating a document with no `name` field or with `name` set to `None` or a non‑string (e.g., `{'name': 123}`), then the result is `False` and no exception is raised.
- AC-4 (FR-2): Given a Query built with `where('name').endswith('son')`, when evaluating a document `{'name': 'Jackson'}`, then the result is `True`.
- AC-5 (FR-2): Given the same query, when evaluating a document `{'name': 'Jack'}`, then the result is `False`.
- AC-6 (FR-2): Given the same query, when evaluating a document with missing, `None`, or non‑string `name`, then the result is `False` and no exception is raised.

## Assumptions and open questions
- A-1 [ASSUMED] The new methods should be cache‑able like existing comparison methods, i.e., they must supply a deterministic hash value based on operation name, field path, and argument. Impact if wrong: query cache may be ineffective or produce incorrect cache keys.
- A-2 [ASSUMED] No existing tests depend on the exact ordering or formatting of docstrings; adding docstrings is safe.

## Non-goals
- Adding
