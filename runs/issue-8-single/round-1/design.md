# Design
## Approach
Modify `Table.remove` to handle the case where both `cond` and `doc_ids` are supplied. The new logic first filters the provided IDs to those that exist, then applies the query (if any) to keep only IDs that satisfy both conditions. The removal is performed atomically via the existing `_update_table` helper, and the method returns the list of actually removed IDs. Existing branches for only‑`doc_ids` or only‑`cond` are left untouched.
## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/table.py | Table.remove | Add handling for `cond` and `doc_ids` together: compute intersection of existing IDs and query match, delete those IDs, return list. | AC-1 |
| tests/test_autose_remove.py | – | New test file covering AC‑1, AC‑2, AC‑3. | AC-1, AC-2, AC-3 |
## Existing tests affected
- None (new tests only).
## Risks
- Slight risk of altering performance of `remove` when both parameters are given, but logic is straightforward.
- Ensure that the atomicity of removal (single `_update_table` call) is preserved.
