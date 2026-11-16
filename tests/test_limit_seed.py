from tinydb import where


def test_limit_returns_first_matches(db):
    db.insert_multiple([{'a': 1, 'i': i} for i in range(5)])
    assert [d['i'] for d in db.search(where('a') == 1, limit=2)] == [0, 1]


def test_limit_none_returns_all(db):
    db.insert_multiple([{'a': 1}] * 4)
    assert len(db.search(where('a') == 1)) == 4
    assert len(db.search(where('a') == 1, limit=None)) == 4


def test_limit_on_named_table(db):
    t = db.table('t')
    t.insert_multiple([{'a': 1}] * 3)
    assert len(t.search(where('a') == 1, limit=2)) == 2
