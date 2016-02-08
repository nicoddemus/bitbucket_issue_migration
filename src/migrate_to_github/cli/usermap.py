import click
from pathlib2 import Path
from migrate_to_github.utils import load, dump
from migrate_to_github.usermap import UserMap


@click.command()
@click.argument('usermaps', type=Path, nargs=-1)
def main(usermaps):

    loaded = {path: load(path) for path in usermaps}
    UserMap.sync_all(loaded.values())
    for path, value in loaded.items():
        dump(value, path)

