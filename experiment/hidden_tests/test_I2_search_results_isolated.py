from tinydb import where
from tinydb.table import Document


def test_mutating_result_key_does_not_change_next_search(db):
    db.insert({'a': 1, 'b': 'keep'})
    first = db.search(where('a') == 1)
    first[0]['b'] = 'changed'
    assert db.search(where('a') == 1)[0]['b'] == 'keep'


def test_mutating_nested_value_does_not_change_next_search(db):
    db.insert({'a': 1, 'n': {'x': [1]}})
    first = db.search(where('a') == 1)
    first[0]['n']['x'].append(2)
    assert db.search(where('a') == 1)[0]['n']['x'] == [1]


def test_storage_is_not_changed_by_mutating_a_result(db):
    db.insert({'a': 1, 'b': 'keep'})
    db.search(where('a') == 1)[0]['b'] = 'changed'
    assert db.all()[0]['b'] == 'keep'


def test_results_still_documents_with_ids(db):
    ids = db.insert_multiple([{'a': 1}, {'a': 1}])
    for _ in range(2):
        res = db.search(where('a') == 1)
        assert all(isinstance(d, Document) for d in res)
        assert [d.doc_id for d in res] == ids
