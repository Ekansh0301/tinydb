import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb import where

# AC-1: None values are skipped in comparison

def test_ac1_none_skipped():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'price': None})
    tbl.insert({'price': 10})
    tbl.insert({'price': 30})
    result = tbl.search(where('price') < 20)
    assert result == [{'price': 10}]

# AC-2: non‑comparable types are skipped

def test_ac2_non_comparable_skipped():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'price': 'free'})
    tbl.insert({'price': 5})
    tbl.insert({'price': 25})
    result = tbl.search(where('price') >= 10)
    assert result == [{'price': 25}]

# AC-3: missing key is skipped

def test_ac3_missing_key_skipped():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    tbl.insert({'cost': 15})
    tbl.insert({'price': 12})
    result = tbl.search(where('price') < 20)
    assert result == [{'price': 12}]

# AC-4: order preserved

def test_ac4_order_preserved():
    db = TinyDB(storage=MemoryStorage)
    tbl = db.table('t')
    doc1 = {'price': 10}
    doc2 = {'price': 20}
    doc3 = {'price': 30}
    tbl.insert(doc1)
    tbl.insert(doc2)
    tbl.insert(doc3)
    result = tbl.search(where('price') < 100)
    assert result == [doc1, doc2, doc3]

# end of tests