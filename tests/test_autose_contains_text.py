import pytest
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

# AC-1: only Jackson matches

def test_ac1_only_jackson_matches():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'name': 'Jackson'}, {'name': 'Emily'}])
    result = db.search(where('name').contains_text('son'))
    assert result == [{'name': 'Jackson'}]

# AC-2: case sensitivity

def test_ac2_case_sensitive():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'Jackson'})
    result = db.search(where('name').contains_text('SON'))
    assert result == []

# AC-3: non-string values yield no match and no error

def test_ac3_non_string_no_match():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': 30}, {'name': None}, {}])
    result = db.search(where('name').contains_text('son'))
    assert result == []

# AC-4: substring at start

def test_ac4_substring_start():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'sonic'})
    result = db.search(where('name').contains_text('son'))
    assert result == [{'name': 'sonic'}]

# AC-5: composable with and

def test_ac5_composable_and():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'name': 'Jackson', 'active': True}, {'name': 'Jackson', 'active': False}])
    result = db.search((where('name').contains_text('son')) & (where('active') == True))
    assert result == [{'name': 'Jackson', 'active': True}]

# end of tests
