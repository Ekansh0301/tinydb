from tinydb import where


def _names(res):
    return [d['name'] for d in res]


def test_startswith(db):
    db.insert_multiple([{'name': n} for n in ['Alice', 'Alan', 'bob', 'Malcolm']])
    assert _names(db.search(where('name').startswith('Al'))) == ['Alice', 'Alan']


def test_endswith(db):
    db.insert_multiple([{'name': n} for n in ['Alice', 'Bruce', 'bob', 'Malcolm']])
    assert _names(db.search(where('name').endswith('ce'))) == ['Alice', 'Bruce']


def test_non_string_and_missing_values_do_not_match_or_raise(db):
    db.insert_multiple([{'name': 5}, {'name': None}, {'x': 1}, {'name': 'Al'}])
    assert _names(db.search(where('name').startswith('A'))) == ['Al']
    assert _names(db.search(where('name').endswith('l'))) == ['Al']


def test_different_arguments_are_not_confused_by_the_cache(db):
    db.insert_multiple([{'name': n} for n in ['Alice', 'Bob', 'Anna']])
    assert _names(db.search(where('name').startswith('A'))) == ['Alice', 'Anna']
    assert _names(db.search(where('name').startswith('B'))) == ['Bob']
    assert _names(db.search(where('name').endswith('a'))) == ['Anna']
    assert _names(db.search(where('name').endswith('e'))) == ['Alice']


def test_case_sensitive_and_combinable(db):
    db.insert_multiple([{'name': 'alice', 'k': 1}, {'name': 'Alice', 'k': 2}])
    assert len(db.search(where('name').startswith('A'))) == 1
    assert len(db.search(where('name').startswith('a') | (where('k') == 2))) >= 1
    assert len(db.search(where('name').startswith('A') & (where('k') == 2))) == 1
