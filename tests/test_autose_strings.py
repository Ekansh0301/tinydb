import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: startswith matches only prefix

def test_ac1_startswith_basic():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'name': 'Alice'})
    tbl.insert({'name': 'Bob'})
    res = tbl.search(where('name').startswith('Al'))
    assert res == [{'name': 'Alice'}]

# AC-2: endswith matches only suffix

def test_ac2_endswith_basic():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'name': 'Jackson'})
    tbl.insert({'name': 'John'})
    res = tbl.search(where('name').endswith('son'))
    assert res == [{'name': 'Jackson'}]

# AC-3: non-string fields are ignored, no exception

def test_ac3_nonstring_start():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'name': 'Alice'})
    tbl.insert({})
    tbl.insert({'name': None})
    tbl.insert({'name': 123})
    res = tbl.search(where('name').startswith('Al'))
    assert res == [{'name': 'Alice'}]

# AC-4: non-string fields ignored for endswith

def test_ac4_nonstring_end():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'name': 'Alice'})
    tbl.insert({})
    tbl.insert({'name': None})
    tbl.insert({'name': 123})
    res = tbl.search(where('name').endswith('ice'))
    assert res == [{'name': 'Alice'}]

# AC-5: case-sensitive

def test_ac5_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'name': 'alice'})
    tbl.insert({'name': 'Alice'})
    res = tbl.search(where('name').startswith('Al'))
    assert res == [{'name': 'Alice'}]

# end of tests
