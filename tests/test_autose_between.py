import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from tinydb.queries import where

# AC-1: between matches inclusive bounds and ignores missing/None

def test_ac1_between_matches_and_excludes_missing():
    db = TinyDB(storage=MemoryStorage)
    docs = [
        {'price': 15},
        {'price': 10},
        {'price': 20},
        {'price': 9},
        {'price': None},
        {},
    ]
    for d in docs:
        db.insert(d)
    result = db.search(where('price').between(10, 20))
    prices = sorted([d['price'] for d in result])
    assert prices == [10, 15, 20]

# AC-2: string comparison

def test_ac2_between_string():
    q = where('name').between('alice', 'charlie')
    assert q({'name': 'bob'}) is True

# AC-3: out of range

def test_ac3_between_out_of_range():
    q = where('price').between(10, 20)
    assert q({'price': 25}) is False

# AC-4: hash stability

def test_ac4_hash_stability():
    q = where('price').between(5, 10)
    h1 = hash(q)
    h2 = hash(q)
    assert h1 == h2

# AC-5: equality and dict key

def test_ac5_query_equality_in_dict():
    q1 = where('price').between(5, 10)
    q2 = where('price').between(5, 10)
    d = {q1: 'a', q2: 'b'}
    assert len(d) == 1
    assert d[q1] == 'b'

# end of tests
