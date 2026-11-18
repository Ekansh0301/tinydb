import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# Helper to create table with n docs, m matching

def create_docs(db, n, m, type_value='log'):
    for i in range(n):
        db.insert({'type': type_value if i < m else 'other', 'id': i})

@pytest.fixture
def db():
    db_ = TinyDB(storage=MemoryStorage)
    db_.drop_tables()
    return db_

# AC-1

def test_ac1_limit_returns_exactly_limit(db):
    create_docs(db, 20, 15)
    res = db.search(where('type') == 'log', limit=10)
    assert len(res) == 10
    assert all(doc['type'] == 'log' for doc in res)
    # order check: ids 0-9
    assert [doc['id'] for doc in res] == list(range(10))

# AC-2

def test_ac2_limit_fewer_than_limit(db):
    create_docs(db, 5, 5)
    res = db.search(where('type') == 'log', limit=10)
    assert len(res) == 5
    assert all(doc['type'] == 'log' for doc in res)
    assert [doc['id'] for doc in res] == list(range(5))

# AC-3

def test_ac3_no_limit_returns_all(db):
    create_docs(db, 10, 7)
    res = db.search(where('type') == 'log')
    assert len(res) == 7
    assert all(doc['type'] == 'log' for doc in res)
    assert [doc['id'] for doc in res] == list(range(7))

# AC-4

def test_ac4_named_table_limit(db):
    logs = db.table('logs')
    create_docs(logs, 30, 30)
    res = logs.search(where('type') == 'log', limit=5)
    assert len(res) == 5
    assert all(doc['type'] == 'log' for doc in res)
    assert [doc['id'] for doc in res] == list(range(5))

# end of tests