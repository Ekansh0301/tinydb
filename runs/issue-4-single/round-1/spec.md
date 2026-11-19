# Spec
## Source statements
S1: “When I run `db.search(where('price') < 20)` I get `TypeError: '<' not supported between instances of 'NoneType' and 'int'`.  
S2: “I expected it to just skip the items without a price, the same way it already skips documents that don't have a `price` key at all.”  
S3: “Same thing happens with `>`, `<=` and `>=`, and when a field holds a mix of strings and numbers.”

## Requirements
- FR-1 [STATED] Comparison queries (`<`, `<=`, `>`, `>=`) must ignore documents whose field value is `None` instead of raising `TypeError`. (S1, S2)
- FR-2 [STATED] Comparison queries must also ignore documents whose field value is of a type that cannot be compared with the right‑hand side (e.g., a string when comparing with a number). (S3)

## Acceptance criteria
- AC-1 (FR-1): Given a table containing documents `{'price': None}` and `{'price': 10}`, when `db.search(where('price') < 20)` is executed, then the result list contains only the document with price 10.
- AC-2 (FR-1): Given a table containing a document without the `price` key and a document with `price` None, when `where('price') > 5` is executed, then the result list is empty (both documents are skipped).
- AC-3 (FR-2): Given a table containing `{'price': 'free'}` and `{'price': 10}`, when `where('price') < 20` is executed, then the result list contains only the document with price 10 (the string value is skipped without error).
- AC-4 (FR-2): Given a table containing `{'price': 'free'}` and `{'price': 10}`, when `where('price') >= 10` is executed, then the result list contains both documents (the string is skipped for the `>=` test but the numeric document matches).

## Assumptions and open questions
- A-1 [ASSUMED] The library’s public API for building queries (`where`) is unchanged; only the internal comparison logic needs adjustment.
- A-2 [ASSUMED] Existing tests rely on the current behaviour for equality/inequality comparisons, which should remain unchanged.

## Non-goals
- Changing behaviour of `==` / `!=` operators.
- Adding new query operators or user‑configurable handling of type mismatches.
