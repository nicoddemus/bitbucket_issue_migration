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
