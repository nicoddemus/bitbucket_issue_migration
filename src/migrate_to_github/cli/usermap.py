import click
from pathlib2 import Path
from migrate_to_github.utils import load, dump
from ..usermap import sync_all

from collections import Counter


def stats(elems):
    counts = Counter(elems)
    return "true: {ntrue} unknown: {nunknown}".format(
        ntrue=counts[True],
        nunknown=counts[None],
    )


@click.command()
@click.argument('usermaps', type=Path, nargs=-1)
def main(usermaps):

    loaded = {path: load(path) for path in usermaps}
    sync_all(loaded.values())
    for path, value in loaded.items():
        dump(value, path)

    mapstats(loaded.items())


def mapstats(elems):
    all_ = {}
    for path, data in elems:
        print(path, stats(data.values()))
        all_.update(data)

    print("all -", stats(all_.values()))
