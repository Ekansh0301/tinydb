import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: only Jackson matches

def test_ac1_only_jackson_matches():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert_multiple([{'name': 'Jackson'}, {'name': 'Emily'}])
    result = db.search(where('name').contains_text('son'))
    assert result == [{'name': 'Jackson'}]

# AC-2: case-sensitive

def test_ac2_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': 'Jackson'})
    result = db.search(where('name').contains_text('SON'))
    assert result == []

# AC-3: non-string fields

def test_ac3_non_string_fields():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert_multiple([{'age': 30}, {'name': None}, {}])
    result = db.search(where('name').contains_text('son'))
    assert result == []

# AC-4: substring at start

def test_ac4_substring_start():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert({'name': 'sonic'})
    result = db.search(where('name').contains_text('son'))
    assert result == [{'name': 'sonic'}]

# AC-5: composability

def test_ac5_composability():
    db = TinyDB(storage=MemoryStorage)
    db.table('t').insert_multiple([
        {'name': 'Jackson', 'active': True},
        {'name': 'Jackson', 'active': False}
    ])
    result = db.search((where('name').contains_text('son')) & (where('active').equals(True)))
    assert result == [{'name': 'Jackson', 'active': True}]

# end of tests