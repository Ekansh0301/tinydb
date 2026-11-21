import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: contains_text matches when substring present

def test_ac1_contains_text_matches():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': 'Jackson'})
    result = db.table('t').search(where('name').contains_text('son'))
    assert {'name': 'Jackson'} in result

# AC-2: case-sensitive

def test_ac2_contains_text_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': 'Jackson'})
    result = db.table('t').search(where('name').contains_text('Son'))
    assert {'name': 'Jackson'} not in result

# AC-3: missing field

def test_ac3_missing_field_no_match():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'age': 30})
    result = db.table('t').search(where('name').contains_text('son'))
    assert result == []

# AC-4: None value

def test_ac4_none_value_no_match():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': None})
    result = db.table('t').search(where('name').contains_text('son'))
    assert result == []

# AC-5: non-string value

def test_ac5_non_string_no_match():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': 12345})
    result = db.table('t').search(where('name').contains_text('son'))
    assert result == []

# end of tests