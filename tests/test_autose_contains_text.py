import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: matches when substring present

def test_ac1_matches_substring():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Jackson'})
    result = db.search(where('name').contains_text('son'))
    assert len(result) == 1
    assert result[0]['name'] == 'Jackson'

# AC-2: case-sensitive

def test_ac2_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Jackson'})
    result = db.search(where('name').contains_text('Son'))
    assert len(result) == 0

# AC-3: missing field

def test_ac3_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'age': 30})
    result = db.search(where('name').contains_text('son'))
    assert len(result) == 0

# AC-4: None value

def test_ac4_none_value():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': None})
    result = db.search(where('name').contains_text('son'))
    assert len(result) == 0

# AC-5: non-string value

def test_ac5_non_string_value():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 12345})
    result = db.search(where('name').contains_text('son'))
    assert len(result) == 0

# end of tests