from tinydb import where


def test_less_than_skips_none(db):
    db.insert_multiple([{'a': 1}, {'a': None}, {'a': 5}, {}])
    assert [d['a'] for d in db.search(where('a') < 3)] == [1]
