import pytest
from tinydb import where


@pytest.fixture
def filled(db):
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}])
    return db


def _call(fn):
    try:
        fn()
    except (ValueError, TypeError, RuntimeError):
        pass  # rejecting the combination is an acceptable answer


def test_remove_never_deletes_a_document_that_does_not_match_the_query(filled):
    _call(lambda: filled.remove(where('a') == 1, doc_ids=[2]))
    assert {d['a'] for d in filled.all()} >= {2, 3, 4}


def test_update_never_changes_a_document_that_does_not_match_the_query(filled):
    _call(lambda: filled.update({'x': 1}, where('a') == 1, doc_ids=[2]))
    assert 'x' not in filled.get(doc_id=2)


def test_other_documents_are_untouched(filled):
    _call(lambda: filled.remove(where('a') == 1, doc_ids=[2]))
    assert len(filled.get(doc_id=3)) == 1 and len(filled.get(doc_id=4)) == 1


def test_single_argument_forms_still_work(filled):
    assert filled.remove(where('a') == 1) == [1]
    assert filled.remove(doc_ids=[2]) == [2]
    assert filled.update({'x': 1}, where('a') == 3) == [3]
    assert filled.update({'y': 1}, doc_ids=[4]) == [4]
