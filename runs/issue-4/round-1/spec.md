# Spec
## Source statements
S1: “I use TinyDB for a small inventory app. Some items don't have a price yet, so I store `None`.”  
S2: “When I run `db.search(where('price') < 20)` I get `TypeError: '<' not supported between instances of 'NoneType' and 'int'`.”  
S3: “I expected it to just skip the items without a price, the same way it already skips documents that don't have a `price` key at all.”  
S4: “Right now one `None` in the table breaks every range query on that field.”  
S5: “Same thing happens with `>`, `<=` and `>=`, and when a field holds a mix of strings and numbers.”  
S6: “Version: the current main.”

## Requirements
- FR-1 [STATED] The system shall treat a field value of `None` as non‑existent for comparison operators `<`, `<=`, `>`, `>=` and therefore **skip** the document rather than raising an exception. (S2, S3)  
- FR-2 [STATED] The system shall treat a field whose value type is not comparable with the right‑hand‑side operand (e.g., a string compared to a number) as non‑existent for the same comparison operators and skip the document without raising an exception. (S5)  
- FR-3 [INFERRED] The system would preserve the existing behaviour of skipping documents that completely lack the queried key for these comparison operators. (S3)  
- FR-4 [ASSUMED] The system would return results in the same order as the underlying table iteration (i.e., insertion order) for consistency with current TinyDB semantics. Impact if wrong: downstream code relying on order may see reordered results. Question: Does TinyDB guarantee order for `search` results?  

## Acceptance criteria
- AC-1 (FR-1): Given a table containing documents `{'price': None}`, `{'price': 10}`, and `{'price': 30}`, when `db.search(where('price') < 20)` is executed, then the result list contains only the document `{'price': 10}` and no exception is raised.  
- AC-2 (FR-2): Given a table containing documents `{'price': 'free'}`, `{'price': 5}`, and `{'price': 25}`, when `db.search(where('price') >= 10)` is executed, then the result list contains only the document `{'price': 25}` and no exception is raised.  
- AC-3 (FR-3): Given a table containing documents `{'cost': 15}` (no `price` key) and `{'price': 12}`, when `db.search(where('price') < 20)` is executed, then the result list contains only the document `{'price': 12}` and no exception is raised.  
- AC-4 (FR-4): Given a table with insertion order `[doc1, doc2, doc3]` where all three satisfy `where('price') < 100`, when `db.search(where('price') < 100)` is executed, then the result list order is `[doc1, doc2, doc3]`.  

## Assumptions and open questions
- A-1 [ASSUMED] The comparison functions (`<`, `<=`, `>`, `>=`) are implemented via the lambda `value < rhs` etc. in `tinydb/queries.py`. Changing them to first check `isinstance(value, (int, float, Decimal))` will not affect other query types. Impact if wrong: May unintentionally filter out valid numeric subclasses (e.g., `fractions.Fraction`). Question: Should the type check be limited to `numbers.Number`?  

## Non-goals
- Changing the behaviour of equality (`==`) or inequality (`!=`) operators for `None` values.  
- Providing automatic type conversion (e.g., converting numeric strings to numbers).  
- Modifying the storage format or migration of existing databases.
