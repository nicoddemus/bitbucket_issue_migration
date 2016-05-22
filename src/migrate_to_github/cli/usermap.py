import click
from pathlib2 import Path
from migrate_to_github.utils import load, dump
from ..usermap import sync_all


@click.command()
@click.argument('usermaps', type=Path, nargs=-1)
def main(usermaps):

    loaded = {path: load(path) for path in usermaps}
    sync_all(loaded.values())
    for path, value in loaded.items():
        dump(value, path)
