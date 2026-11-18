import pytest
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

# AC-1: startswith matches only prefix

def test_ac1_startswith_basic():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Alice'})
    db.insert({'name': 'Bob'})
    q = Query()
    res = db.search(q.name.startswith('Al'))
    assert res == [{'name': 'Alice'}]

# AC-2: endswith matches only suffix

def test_ac2_endswith_basic():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Jackson'})
    db.insert({'name': 'John'})
    q = Query()
    res = db.search(q.name.endswith('son'))
    assert res == [{'name': 'Jackson'}]

# AC-3: non-string fields ignored, no exception

def test_ac3_nonstring_startswith():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Alice'})
    db.insert({})
    db.insert({'name': None})
    db.insert({'name': 123})
    q = Query()
    res = db.search(q.name.startswith('Al'))
    assert res == [{'name': 'Alice'}]

# AC-4: non-string fields ignored for endswith

def test_ac4_nonstring_endswith():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Alice'})
    db.insert({})
    db.insert({'name': None})
    db.insert({'name': 123})
    q = Query()
    res = db.search(q.name.endswith('ice'))
    assert res == [{'name': 'Alice'}]

# AC-5: case-sensitive

def test_ac5_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'alice'})
    db.insert({'name': 'Alice'})
    q = Query()
    res = db.search(q.name.startswith('Al'))
    assert res == [{'name': 'Alice'}]

# end of tests
