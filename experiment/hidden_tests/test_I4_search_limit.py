from tinydb import where


def test_limit_returns_first_matches_in_insertion_order(db):
    db.insert_multiple([{'a': 1, 'i': i} for i in range(5)])
    assert [d['i'] for d in db.search(where('a') == 1, limit=2)] == [0, 1]


def test_limit_zero_and_larger_than_matches(db):
    db.insert_multiple([{'a': 1}, {'a': 1}])
    assert db.search(where('a') == 1, limit=0) == []
    assert len(db.search(where('a') == 1, limit=10)) == 2


def test_default_is_unlimited(db):
    db.insert_multiple([{'a': 1}] * 7)
    assert len(db.search(where('a') == 1)) == 7
    assert len(db.search(where('a') == 1, limit=None)) == 7


def test_cache_is_not_confused_by_limit(db):
    db.insert_multiple([{'a': 1, 'i': i} for i in range(4)])
    q = where('a') == 1
    assert len(db.search(q, limit=1)) == 1
    assert len(db.search(q)) == 4
    assert len(db.search(q, limit=2)) == 2
    assert len(db.search(q)) == 4


def test_works_on_named_tables(db):
    t = db.table('t')
    t.insert_multiple([{'a': 1}, {'a': 1}, {'a': 1}])
    assert len(t.search(where('a') == 1, limit=2)) == 2
