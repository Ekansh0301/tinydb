import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# Helper to create table with docs

def create_docs(db, count, match=True):
    for i in range(count):
        db.insert({'type': 'log' if match else 'other', 'id': i})

# AC-1

def test_ac1_limit_returns_exactly_limit():
    db = TinyDB(storage=MemoryStorage)
    create_docs(db, 20, match=True)
    # 15 match, but we insert 20 all match
    # Actually need 15 match, 5 non
    db.drop_tables()
    for i in range(15):
        db.insert({'type': 'log', 'id': i})
    for i in range(5):
        db.insert({'type': 'other', 'id': 15+i})
    result = db.search(where('type') == 'log', limit=10)
    assert len(result) == 10
    assert all(doc['type'] == 'log' for doc in result)
    # order check: ids 0-9
    assert [doc['id'] for doc in result] == list(range(10))

# AC-2

def test_ac2_limit_greater_than_matches():
    db = TinyDB(storage=MemoryStorage)
    for i in range(5):
        db.insert({'type': 'log', 'id': i})
    result = db.search(where('type') == 'log', limit=10)
    assert len(result) == 5
    assert [doc['id'] for doc in result] == list(range(5))

# AC-3

def test_ac3_no_limit_returns_all():
    db = TinyDB(storage=MemoryStorage)
    for i in range(7):
        db.insert({'type': 'log', 'id': i})
    result = db.search(where('type') == 'log')
    assert len(result) == 7
    assert [doc['id'] for doc in result] == list(range(7))

# AC-4

def test_ac4_named_table_limit():
    db = TinyDB(storage=MemoryStorage)
    logs = db.table('logs')
    for i in range(30):
        logs.insert({'type': 'log', 'id': i})
    result = logs.search(where('type') == 'log', limit=5)
    assert len(result) == 5
    assert [doc['id'] for doc in result] == list(range(5))

# end of tests
