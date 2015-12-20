import json as serializer
import requests
import click
from functools import partial

progress = partial(click.progressbar, show_pos=True, show_percent=True)


def gprocess(iterator, *k, **kw):
    with progress(iterator, *k, **kw) as bar:
        yield from bar


NOT_GIVEN = object()
PRETTY = {'sort_keys': True, 'indent': 2}
BB_METADATA = 'bb-metadata'
USERMAP = 'map-bb-to-gh'


# TODO: needs a better place
GITHUB_REPO_IMPORT_API = 'https://api.github.com/repos/{repo}/import/issues'


def dump(data, path, join=None, **format_args):
    if join is not None:
        path = path / join.format(**format_args)
    with path.open('w') as fp:
        serializer.dump(data, fp, **PRETTY)


def load(path, default=NOT_GIVEN):
    try:
        fp = path.open()
    except IOError:
        if default is not NOT_GIVEN:
            return default
        raise
    else:
        with fp:
            return serializer.load(fp)


class Getter(object):
    def __init__(self, base_url, **args):
        self.session = requests.Session()
        self.base_url = base_url.format(**args)

    def __call__(self, url):
        return self.session.get(self.base_url + url).json()


def debug(data):
    data = dict(data)
    click.echo(serializer.dumps(data, **PRETTY))


def contributor(key, item):
    if item.get(key):
        return item[key]['username']


def maybe_contributors(issue, comments):
    yield contributor('reported_by', issue)
    yield from (
        contributor('author_info', comment)
        for comment in comments)


def contributors(issue, comments):
    return filter(None, maybe_contributors(issue, comments))
