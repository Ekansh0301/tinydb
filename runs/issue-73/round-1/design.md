# Design
## Approach
Add a new query operator `contains_text` to the `Query` class, mirroring the existing `matches` and `search` implementations but performing a simple case‑sensitive substring test. The operator will safely ignore non‑string values, missing fields, or `None` by returning `False`. By using `_generate_test` with a hash tuple that includes the operation name, field path, and substring, the new operator integrates with TinyDB’s query‑caching mechanism without affecting other components.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/queries.py | `Query.contains_text` (NEW method) | Implement substring check: verify value is `str`; return `substring in value`. Register hash tuple `('contains_text', self._path, substring)`. Add docstring and usage example. | AC-1, AC-2, AC-3, AC-4, AC-5 |
| tinydb/queries.py | `Query` class docstring (optional) | Mention new operator in the class description. | AC-1‑5 (no code change needed) |

## Existing tests affected
None. The new operator is additive; existing tests for `matches`, `search`, and other operators remain unchanged.

## Risks
- **Cache hash collision**: Incorrect hash tuple could cause different queries to share a cache entry. Using a distinct operation name `'contains_text'` avoids this.
- **Performance**: Simple substring check is O(n) on the field value length, but this mirrors existing regex searches and is acceptable for TinyDB’s typical workloads.
- **Future API changes**: Adding the method directly to `Query` may require updating any generated documentation, but it does not impact storage or table logic.
