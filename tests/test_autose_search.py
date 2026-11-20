import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: limit returns at most limit documents

def test_ac1_limit_returns_at_most_limit():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple({'type': 'log', 'msg': i} for i in range(10))
    results = db.search(where('type') == 'log', limit=5)
    assert len(results) <= 5
    assert all(isinstance(r, type(db.all()[0])) for r in results)

# AC-2: order preserved

def test_ac2_order_preserved_with_limit():
    db = TinyDB(storage=MemoryStorage)
    docs = [{'type': 'log', 'msg': i} for i in range(6)]
    db.insert_multiple(docs)
    results = db.search(where('type') == 'log', limit=3)
    assert results == [db.all()[i] for i in range(3)]

# AC-3: no limit returns all

def test_ac3_no_limit_returns_all():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple({'type': 'log', 'msg': i} for i in range(8))
    results = db.search(where('type') == 'log')
    assert len(results) == 8
    assert results == db.all()

# AC-4: named table limit

def test_ac4_named_table_limit():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('my_table')
    table.insert_multiple({'type': 'log', 'msg': i} for i in range(12))
    results = table.search(where('type') == 'log', limit=4)
    assert len(results) == 4
    assert results == [table.all()[i] for i in range(4)]

# end of tests
