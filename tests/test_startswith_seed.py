from tinydb import where


def test_startswith(db):
    db.insert_multiple([{'name': n} for n in ['Alice', 'Alan', 'bob']])
    assert [d['name'] for d in db.search(where('name').startswith('Al'))] == ['Alice', 'Alan']


def test_endswith(db):
    db.insert_multiple([{'name': n} for n in ['Alice', 'Bruce', 'bob']])
    assert [d['name'] for d in db.search(where('name').endswith('ce'))] == ['Alice', 'Bruce']


def test_non_strings_do_not_match(db):
    db.insert_multiple([{'name': 5}, {'name': None}, {'x': 1}, {'name': 'Al'}])
    assert [d['name'] for d in db.search(where('name').startswith('A'))] == ['Al']
