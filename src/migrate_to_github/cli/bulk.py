from pathlib2 import Path
import click

from . import commands
from ..store import FileStore
from .usermap import sync_usermaps


@click.group(chain=True)
def main():
    pass


def map_stores(paths, func):
    for path in paths:
        store = FileStore.open(path)
        click.echo('Working on {}'.format(path))
        func(store)


def command(function):
    cmd = main.command()
    arg = click.argument("stores", nargs=-1, type=Path)
    return cmd(arg(function))


@command
def fetch(stores):
    map_stores(stores, commands.fetch)


@command
def extract_users(stores):
    map_stores(stores, commands.extract_users)


@command
def convert(stores):
    map_stores(stores, commands.convert)


@command
def sync(stores):
    stores = map(FileStore.open, stores)
    maps = [store.get('users', {}) for store in stores]
    sync_usermaps(maps)
    for store, mapping in zip(stores, maps):
        store['users'] = map
