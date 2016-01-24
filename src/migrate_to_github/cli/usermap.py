import click
from pathlib2 import Path
from migrate_to_github.utils import load, dump


def warn(message, **kwargs):
    click.secho(message.format(**kwargs), fg='yellow', bold=True)


def refresh_usermap(source, target, union=False, _warn=warn):
    for key, value in source.items():
        if value is None:
            continue

        targetvalue = target.get(key)
        if targetvalue is not None and value != targetvalue:
            _warn('for {key} the {targetvalue} !0 {value}',
                  key=key, targetvalue=targetvalue, value=value)
            continue
        if key in target or union:
            target[key] = value


@click.command()
@click.argument('usermaps', type=Path, nargs=-1)
def main(usermaps):

    loaded = {path: load(path) for path in usermaps}
    sync_usermaps(loaded.values())
    for path, value in loaded.items():
        dump(value, path)


def sync_usermaps(mappings):
    merged = {}
    for user_map in mappings:
        refresh_usermap(
                source=user_map, target=merged, union=True)
    for user_map in mappings:
        refresh_usermap(
                source=merged, target=user_map, union=False)
