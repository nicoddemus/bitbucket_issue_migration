import click
from pathlib2 import Path
from .utils import load, dump


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
    merged = {}
    for usermap in loaded.values():
        refresh_usermap(
            source=usermap, target=merged, union=True)

    for usermap in loaded.values():
        refresh_usermap(
            source=merged, target=usermap, union=False)
    for path, value in loaded.items():
        dump(value, path)
