import json as serializer

import requests
import click

NOT_GIVEN = object()
PRETTY = {'sort_keys': True, 'indent': 2}

# TODO: needs a better place
GITHUB_REPO_IMORT_API = 'https://api.github.com/repos/{repo}/import/issues'


def dump(data, path, join=None, **format_args):
    if join is not None:
        path = path.joinpath(join.format(**format_args))
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


def debug(data):
    data = dict(data)
    click.echo(serializer.dumps(data, **PRETTY))


class Getter(object):
    def __init__(self, base_url, **args):
        self.session = requests.Session()
        self.base_url = base_url.format(**args)

    def __call__(self, url):
        return self.session.get(self.base_url + url).json()


class Poster(object):

    def __init__(self, api_token, base_url, **args):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'token ' + api_token,
            'Accept': 'application/vnd.github.golden-comet-preview+json',
            'User-Agent': 'Bulk issue importer 0.1'
        })
        self.base_url = base_url.format(**args)

    def __call__(self,  data):
        response = self.session.post(self.base_url, data=data)
        if response.status_code in (200, 202):
            return response.json()
        else:
            click.echo(response.status_code)
            debug(response.headers)
            debug(response.json())
            raise SystemExit(1)


def progress(items, **kwargs):
    return click.progressbar(
        items, show_pos=True, show_percent=True,
        **kwargs)
