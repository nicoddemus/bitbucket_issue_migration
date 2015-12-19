import attr
from pathlib2 import Path


@attr.s
class FileStore(object):
    path = attr.ib(validator=attr.validators.instance_of(Path))


    @classmethod
    def open(cls, path):
        if path.is_dir():
            return cls(path=path)
        else:
            raise NotADirectoryError(path)


    @classmethod
    def create(cls, path):
        path.mkdir()
        return cls.open(path=path)



