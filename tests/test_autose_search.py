import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: limit returns at most limit docs and each is Document

def test_ac1_limit_returns_at_most_and_documents():
    db = TinyDB(storage=MemoryStorage)
    docs = [{'type': 'log', 'i': i} for i in range(10)]
    db.insert_multiple(docs)
    result = db.search(where('type') == 'log', limit=5)
    assert len(result) <= 5
    for d in result:
        assert hasattr(d, 'doc_id')

# AC-2: preserves order

def test_ac2_limit_preserves_order():
    db = TinyDB(storage=MemoryStorage)
    docs = [{'type': 'log', 'i': i} for i in range(6)]
    db.insert_multiple(docs)
    result = db.search(where('type') == 'log', limit=3)
    assert [d['i'] for d in result] == [0, 1, 2]

# AC-3: no limit returns all

def test_ac3_no_limit_returns_all():
    db = TinyDB(storage=MemoryStorage)
    docs = [{'type': 'log', 'i': i} for i in range(8)]
    db.insert_multiple(docs)
    result = db.search(where('type') == 'log')
    assert len(result) == 8
    assert [d['i'] for d in result] == list(range(8))

# AC-4: named table

def test_ac4_named_table_limit():
    db = TinyDB(storage=MemoryStorage)
    table = db.table('my_table')
    docs = [{'type': 'log', 'i': i} for i in range(12)]
    table.insert_multiple(docs)
    result = table.search(where('type') == 'log', limit=4)
    assert len(result) == 4
    assert [d['i'] for d in result] == [0, 1, 2, 3]

# end of tests
