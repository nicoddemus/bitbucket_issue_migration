import pytest
from pathlib2 import Path
from migrate_to_github.store import FileStore


@pytest.fixture
def tmppath(tmpdir):
    return Path(tmpdir.strpath)


def test_file_store_creation(tmppath):
    new = tmppath / 'test'

    FileStore.open(tmppath)

    with pytest.raises(NotADirectoryError):
        FileStore.open(new)

    with pytest.raises(FileExistsError):
        FileStore.create(tmppath)

    FileStore.create(new)
    FileStore.open(new)


def test_file_store_basic_mapping(tmppath):
    store = FileStore(tmppath)
    assert not list(store)
    assert not len(store)
    store[1] = {}
    assert list(store) == ['1']
    assert len(store) == 1
    assert store[1] == {}

    assert 1 in store

    del store[1]
    with pytest.raises(KeyError):
        store[1]

    assert 1 not in store

