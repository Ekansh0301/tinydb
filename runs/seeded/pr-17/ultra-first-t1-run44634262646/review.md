# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The fix only addresses `__lt__` (less than) but leaves `__le__`, `__gt__`, and `__ge__` vulnerable to the same TypeError when encountering None values. The issue explicitly states all four comparison operators crash. The test only covers `<`, so the other three operators remain broken.

## Checks
- [pass] __lt__ skips None values: python -c "from tinydb import TinyDB, where; from tinydb.storages import MemoryStorage; db = TinyDB(storage=MemoryStorage); db.insert_multiple([{'a': 1}, {'a': None}, {'a': 5}, {}]); print([d['a'] for d in db.search(where('a') < 3)])" -> [1]
- [fail] __le__, __gt__, __ge__ still crash on None: python -c "from tinydb import TinyDB, where; from tinydb.storages import MemoryStorage; db = TinyDB(storage=MemoryStorage); db.insert_multiple([{'a': 1}, {'a': None}, {'a': 5}, {}]); print([d['a'] for d in db.search(where('a') <= 3)])" -> TypeError: '<=' not supported between instances of 'NoneType'

## Findings
- (high) tinydb/queries.py:301 __le__ missing None check - will crash on None values
- (high) tinydb/queries.py:314 __gt__ missing None check - will crash on None values
- (high) tinydb/queries.py:327 __ge__ missing None check - will crash on None values
- (medium) tests/test_none_seed.py:4 Test only covers < operator, not <=, >, >=

_Reviewer model: nvidia:nvidia/nemotron-3-ultra-550b-a55b_
