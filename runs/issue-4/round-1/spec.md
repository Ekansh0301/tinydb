# Spec
## Source statements
S1: "I use TinyDB for a small inventory app. Some items don't have a price yet, so I store `None`."
S2: "When I run `db.search(where('price') < 20)` I get `TypeError: '<' not supported between instances of 'NoneType' and 'int'`."
S3: "I expected it to just skip the items without a price, the same way it already skips documents that don't have a `price` key at all."
S4: "Right now one `None` in the table breaks every range query on that field."
S5: "Same thing happens with `>`, `<=` and `>=`, and when a field holds a mix of strings and numbers."
S6: "Version: the current main."

## Requirements
- FR-1 [STATED] The system shall treat a field value of `None` as absent for the purpose of comparison operators (`<`, `>`, `<=`, `>=`) in a `where` query, so that documents containing `None` in the queried field do not cause a `TypeError` and are simply omitted from the result set. (S2, S3, S4)
- FR-2 [STATED] The system shall treat a missing field (i.e., the key is not present in a document) identically to a field whose value is `None` for comparison operators, skipping such documents without error. (S3)
- FR-3 [STATED] The system shall apply the same skipping behaviour for all range comparison operators supported by the query language: `<`, `>`, `<=`, `>=`. (S5)
- FR-4 [STATED] When a field contains values of heterogeneous, non‑comparable types (e.g., a mix of strings and numbers), the system shall skip any document whose field value cannot be compared with the literal used in the query, rather than raising a `TypeError`. (S5)
- FR-5 [INFERRED] The system would return an empty result set if no documents satisfy the comparison after skipping `None` and non‑comparable values. (S2‑S5)
- FR-6 [ASSUMED] The system would preserve the original ordering semantics of the query (i.e., no implicit sorting is introduced) while performing the skipping logic. Impact if wrong: tests that rely on order may fail; Question: Does TinyDB guarantee any order for `search` results? 

## Acceptance criteria
- AC-1 (FR-1, FR-3): Given a TinyDB table containing documents `{'price': 10}`, `{'price': None}`, `{'price': 30}`, when executing `db.search(where('price') < 20)`, then the result shall be a list containing only `{'price': 10}` and shall not raise any exception.
- AC-2 (FR-2): Given a TinyDB table containing documents `{'price': 5}`, `{}`, `{'price': 15}`, when executing `db.search(where('price') <= 10)`, then the result shall be a list containing only `{'price': 5}` and shall not raise any exception.
- AC-3 (FR-4): Given a TinyDB table containing documents `{'price': 8}`, `{'price': 'free'}`, `{'price': None}`, when executing `db.search(where('price') > 5)`, then the result shall be a list containing only `{'price': 8}` and shall not raise any exception.
- AC-4 (FR-5): Given a TinyDB table containing documents `{'price': None}`, `{'price': 'high'}`, when executing `db.search(where('price') < 0)`, then the result shall be an empty list and shall not raise any exception.
- AC-5 (FR-1, FR-3, FR-4): Given a TinyDB table containing documents `{'price': 12}`, `{'price': None}`, `{'price': '12'}`, `{'price': 8}`, when executing `db.search(where('price') >= 10)`, then the result shall be a list containing `{'price': 12}` only, skipping the `None` and the string `'12'` without error.

## Assumptions and open questions
- A-1 [ASSUMED] The existing `where` implementation uses Python's native comparison operators internally. Impact if wrong: the fix may need to wrap comparisons rather than rely on operator overloading. Question: Does TinyDB currently delegate to Python's `<` etc., or does it have its own comparator that can be patched?
- A-2 [ASSUMED] No existing tests rely on a `TypeError` being raised for `None` values; therefore changing the behaviour will not break backward compatibility. Impact if wrong: existing user code that expects an exception may need to be updated. Question: Are there any documented cases where raising `TypeError` is part of the API contract?
- A-3 [ASSUMED] The change will not affect other query operators (e.g., `==`, `!=`, `exists()`). Impact if wrong: unintended side effects on equality queries. Question: Should equality comparisons also treat `None` as absent, or keep current semantics?

## Non-goals
- Changing the behaviour of equality (`==`) or inequality (`!=`) comparisons for `None` values.
- Introducing automatic type coercion (e.g., converting numeric strings to numbers) for range queries.
- Modifying the storage format or serialization of `None` values.
- Providing user‑configurable policies for handling non‑comparable types; the specification fixes the policy to “skip”.
