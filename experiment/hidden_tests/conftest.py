import pytest
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

@pytest.fixture
def db():
    return TinyDB(storage=MemoryStorage)
