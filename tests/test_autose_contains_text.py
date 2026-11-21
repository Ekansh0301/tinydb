import pytest
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

# AC-1

def test_ac1_contains_text_basic():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'name': 'Jackson'}, {'name': 'Emily'}])
    q = Query()
    result = db.search(q.name.contains_text('son'))
    assert result == [{'name': 'Jackson'}]

# AC-2

def test_ac2_contains_text_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Jackson'})
    q = Query()
    result = db.search(q.name.contains_text('SON'))
    assert result == []

# AC-3

def test_ac3_contains_text_non_string():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': 30}, {'name': None}, {}])
    q = Query()
    result = db.search(q.name.contains_text('son'))
    assert result == []

# AC-4

def test_ac4_contains_text_substring():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'sonic'})
    q = Query()
    result = db.search(q.name.contains_text('son'))
    assert result == [{'name': 'sonic'}]

# AC-5

def test_ac5_contains_text_composable():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'name': 'Jackson', 'active': True}, {'name': 'Jackson', 'active': False}])
    q = Query()
    result = db.search((q.name.contains_text('son')) & (q.active == True))
    assert result == [{'name': 'Jackson', 'active': True}]

# end of tests