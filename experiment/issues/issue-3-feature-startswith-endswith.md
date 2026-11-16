# Add startswith / endswith to Query

For name lookups I keep writing regexes:

```python
db.search(where('name').matches(r'^Al'))
```

It would be nicer to have

```python
db.search(where('name').startswith('Al'))
db.search(where('name').endswith('son'))
```

Only strings should match; documents where the field is missing, `None` or a number should just not match (no error). Case-sensitive is fine.
