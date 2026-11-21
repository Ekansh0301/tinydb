# Design
## Approach
Add a `between(self, low, high)` method to the `Query` class in `tinydb/queries.py`. The method will generate a test that returns `True` only when the field value exists, is not `None`, and lies within the inclusive range `[low, high]`. The hash tuple will be `('between', self._path, low, high)` so that identical between‑queries are equal and cacheable. No other files need modification, and existing tests remain valid.

## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/queries.py | class Query | **NEW method** `def between(self, low, high) -> QueryInstance:` – uses `_generate_test` with a lambda that checks the field is present, not `None`, and `low <= value <= high`; hash tuple `('between', self._path, low, high)`. | AC-1, AC-2, AC-3, AC-4, AC-5 |
| tinydb/queries.py | class Query | No other modifications; existing methods unchanged. | (none) |

## Existing tests affected
none

## Risks
- The lambda must handle values that are not orderable (e.g., lists); such inputs will raise a `TypeError`, which is acceptable because FR‑3 limits usage to numbers and strings.  
- Ensure the hash tuple uses the same ordering as other operators; otherwise caching could be inconsistent.  
- Adding the method must not interfere with existing operator overloads or the `QueryInstance` contract.
