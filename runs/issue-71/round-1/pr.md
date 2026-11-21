Refs #71 (round 1)

## Acceptance criteria
- AC-1: Given a TinyDB instance `db` containing documents `{'price': 15}`, `{'price': 10}`, `{'price': 20}`, `{'price': 9}`, `{'price': None}`, `{}`; when executing `db.search(where('price').between(10, 20))`, then the result list shall contain exactly the three documents with `price` values 10, 15, and 20, in any order.
- AC-2: Given a document `{'name': 'bob'}` and a query `where('name').between('alice', 'charlie')`; when the query is called with the document, then it shall return `True` because `'bob'` lies lexicographically between `'alice'` and `'charlie'`.
- AC-3: Given a document `{'price': 25}` and the same query as AC-1; when the query is called, then it shall return `False`.
- AC-4: Given a `Query` object `q = where('price').between(5, 10)`, when `hash(q)` is computed twice, then the two hash values shall be equal.
- AC-5: Given two identical `between` queries `q1 = where('price').between(5, 10)` and `q2 = where('price').between(5, 10)`, when they are used as keys in a dictionary, then `dict([ (q1, 'a'), (q2, 'b') ])` shall contain a single entry (the second insertion overwrites the first), demonstrating that they are considered equal for caching purposes.

## Changes
```
tests/test_autose_between.py | 53 ++++++++++++++++++++++++++++++++++++++++++++
 tinydb/queries.py            | 13 +++++++++++
 2 files changed, 66 insertions(+)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_between_matches_and_excludes_missing, test_ac2_between_string, test_ac3_between_out_of_range, test_ac4_hash_stability, test_ac5_query_equality_in_dict

- Failing on the base commit (expected for new behaviour): tests/test_autose_between.py::test_ac1_between_matches_and_excludes_missing, tests/test_autose_between.py::test_ac2_between_string, tests/test_autose_between.py::test_ac3_between_out_of_range, tests/test_autose_between.py::test_ac4_hash_stability, tests/test_autose_between.py::test_ac5_query_equality_in_dict
- Tests passing on the new code: 233
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-71/round-1). Tokens used so far: 374296.

Opened by the autose workflow. It never merges; a person decides.
