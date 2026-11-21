# Design
## Approach
Add a `between` method to the `Query` class in `tinydb/queries.py`. The method will generate a test that returns `True` when the document’s field value is greater than or equal to `low` and less than or equal to `high`, handling missing fields or `None` by returning `False` (the existing `_generate_test` already catches `KeyError` and `TypeError`). The hash for caching will include the operation name and frozen bounds, preserving cache identity rules. No other files need modification.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/queries.py | `Query.between` | **NEW** method added to `Query` class: <br>```python<br>def between(self, low: Any, high: Any) -> QueryInstance:<br>    \"\"\"Test that a field value is within the inclusive range [low, high].\"\"\"<br>    return self._generate_test(<br>        lambda value: low <= value <= high,<br>        ('between', self._path, freeze(low), freeze(high))<br>    )<br>```<br>Uses existing `_generate_test` so missing fields or `None` yield `False`. | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 |
| tinydb/queries.py | `Query` class docstring | Updated brief mention of new method in the class description (optional, non‑functional). | none |

## Existing tests affected
none – the new method does not alter existing behaviour; all current tests should continue to pass.

## Risks
- The hash tuple must remain hashable; using `freeze` on both bounds satisfies the cache‑ability rule (C4).  
- If a user passes unhashable mutable objects as bounds, `freeze` will convert them or raise, matching existing behaviour for other operators.  
- No impact on storage or table logic, preserving constraints C1‑C5.
