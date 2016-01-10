from pathlib2 import Path
import pytest


@pytest.fixture
def tmppath(tmpdir):
    return Path(tmpdir.strpath)
