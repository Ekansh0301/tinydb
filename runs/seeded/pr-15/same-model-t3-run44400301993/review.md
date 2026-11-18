# Review

Verdict: **APPROVE**

The change adds startswith and endswith query methods that correctly handle string matching and ignore non-string values, matching the issue request. All existing and new tests pass.

## Checks
- [pass] startswith works for matching strings and ignores non-strings: python -c "from tinydb import TinyDB, where; db=TinyDB(storage=TinyDB.default_storage); db.insert_multiple([{'name': 'Alice'}, {'name': 5}, {'name': None}, {'x':1}]); print([d['name'] for d in db.search(where('name').startswith('Al'))])"
- [pass] endswith works for matching strings: python -c "from tinydb import TinyDB, where; db=TinyDB(storage=TinyDB.default_storage); db.insert_multiple([{'name': 'Alice'}, {'name': 'Bruce'}]); print([d['name'] for d in db.search(where('name').endswith('ce'))])"

## Findings

_Reviewer model: groq:openai/gpt-oss-120b_
