# Design
## Approach
Modify `Table.remove` to handle the case where both `doc_ids` and `cond` are supplied. The existing logic for each case remains unchanged; when both are present we filter the requested IDs by the condition before deletion. No other files are touched.
## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/table.py | Table.remove | Added branch handling both `doc_ids` and `cond`: compute `ids_to_remove` as intersection of existing IDs and those satisfying `cond`; delete them and return the list. Updated comment. | AC-1, AC-2, AC-3 |
| tests/test_autose_remove.py | – | New tests covering removal by IDs only, by condition only, and by both together. | AC-1, AC-2, AC-3 |
## Existing tests affected
None
## Risks
- Risk that the new branch changes semantics when `cond` is falsy but provided; mitigated by explicit `if cond is not None` check.
- Risk of type‑checking issues with `cast(QueryLike, cond)`; retained original pattern to keep MyPy happy.
- Risk of altering atomicity; the updater still collects IDs before deletion, preserving original atomic behaviour.
