from tinydb import where


def test_less_than_skips_none_and_missing(db):
    db.insert_multiple([{'a': 1}, {'a': None}, {'a': 5}, {}])
    assert [d['a'] for d in db.search(where('a') < 3)] == [1]


def test_all_ordering_operators_do_not_raise(db):
    db.insert_multiple([{'a': 1}, {'a': None}, {'a': 5}])
    assert [d['a'] for d in db.search(where('a') > 2)] == [5]
    assert [d['a'] for d in db.search(where('a') <= 1)] == [1]
    assert [d['a'] for d in db.search(where('a') >= 5)] == [5]


def test_mixed_types_do_not_raise(db):
    db.insert_multiple([{'a': 'x'}, {'a': 2}, {'a': None}])
    assert [d['a'] for d in db.search(where('a') < 3)] == [2]


def test_combined_and_inverted_queries(db):
    db.insert_multiple([{'a': 1, 'b': 1}, {'a': None, 'b': 1}, {'a': 5, 'b': 2}])
    assert len(db.search((where('a') < 3) & (where('b') == 1))) == 1
    assert len(db.search(~(where('a') < 3))) == 2
