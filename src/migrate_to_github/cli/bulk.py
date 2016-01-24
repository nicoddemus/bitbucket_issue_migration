from pathlib2 import Path
import click

from . import commands
from ..store import FileStore


@click.group(chain=True)
def main():
    pass


def mapstores(paths, func):
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
    mapstores(stores, commands.fetch)


@command
def extract_users(stores):
    mapstores(stores, commands.extract_users)


@command
def convert(stores):
    mapstores(stores, commands.convert)
