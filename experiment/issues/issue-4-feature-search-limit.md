# Option to limit the number of results of search()

When I show results in a UI I only need the first few matches, but `search()` always returns everything:

```python
first_ten = db.search(where('type') == 'log')[:10]
```

Could `search()` take an optional `limit` argument so that

```python
db.search(where('type') == 'log', limit=10)
```

returns at most 10 documents, in the order they are stored? Without `limit` nothing should change. It should work on named tables too.
