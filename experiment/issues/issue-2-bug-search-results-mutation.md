# Editing a document I got from search() changes what the next search returns

I fetch some documents, tweak them in memory for a report, and don't call `update()`:

```python
users = db.search(where('team') == 'red')
users[0]['name'] = 'REDACTED'      # only for the printout
...
db.search(where('team') == 'red')[0]['name']   # -> 'REDACTED'
```

The file on disk is untouched, but the second `search()` with the same query returns the edited name. If I change something nested (e.g. append to a list inside a document) the same thing happens. It took me a while to work out that the results come from some cache. I'd expect the documents I get back to be mine to modify without affecting later searches or the database.
