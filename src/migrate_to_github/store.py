import attr
from pathlib2 import Path
from .utils import load, dump
from collections import MutableMapping


@attr.s
class FileStore(MutableMapping):
    path = attr.ib(validator=attr.validators.instance_of(Path))

    @classmethod
    def open(cls, path):
        if path.is_dir():
            return cls(path=path)
        else:
            raise NotADirectoryError(path)

    @classmethod
    def ensure(cls, path):
        path.mkdir(exist_ok=True, parents=True)
        return cls.open(path=path)

    @classmethod
    def create(cls, path):
        path.mkdir()
        return cls.open(path=path)

    def __len__(self):
        return len(list(self.path.glob('*.json')))

    def __iter__(self):
        for path in self.path.glob('*.json'):
            yield path.stem

    def _keypath(self, key):
        realkey = '{}.json'.format(key)
        return self.path / realkey

    def raw_data(self, key):
        return self._keypath(key).read_bytes()

    def __setitem__(self, key, value):
        dump(value, self._keypath(key))
        return self

    def __getitem__(self, key):
        try:
            return load(self._keypath(key))
        except FileNotFoundError as not_found:
            raise KeyError(key) from not_found

    def __delitem__(self, key):
        self._keypath(key).unlink()
