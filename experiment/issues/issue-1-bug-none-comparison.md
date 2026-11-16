# search with < or > crashes when some documents have None in that field

I use TinyDB for a small inventory app. Some items don't have a price yet, so I store `None`.
When I run

```python
db.search(where('price') < 20)
```

I get

```
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

I expected it to just skip the items without a price, the same way it already skips documents that don't have a `price` key at all. Right now one `None` in the table breaks every range query on that field. Same thing happens with `>`, `<=` and `>=`, and when a field holds a mix of strings and numbers.

Version: the current main.
