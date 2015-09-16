import json as serializer
from datetime import datetime, timedelta
from time import sleep
import requests
import attr
import click
from functools import partial

progress = partial(click.progressbar, show_pos=True, show_percent=True)

NOT_GIVEN = object()
PRETTY = {'sort_keys': True, 'indent': 2}

# TODO: needs a better place
GITHUB_REPO_IMPORT_API = 'https://api.github.com/repos/{repo}/import/issues'


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
        self.limiter = Limiter()
        self.base_url = base_url.format(**args)


    def __call__(self,  data):
        self.limiter.wait_before_request()
        response = self.session.post(self.base_url, data=data)
        self.limiter.process_response(response)
        if response.status_code in (200, 202):
            return response.json()
        else:
            click.echo(response.status_code)
            debug(response.headers)
            debug(response.json())
            raise SystemExit(1)

@attr.s
class Limiter(object):
    _do_sleep = attr.ib(default=sleep, repr=False)
    _current_utctime = attr.ib(default=datetime.utcnow, repr=False)
    remaining = attr.ib(default=None)
    reset_timestamp = attr.ib(default=None)

    def record_rate_limit(self, remaining, reset_timestamp):

        self.remaining = int(remaining)
        self.reset_timestamp = datetime.utcfromtimestamp(int(reset_timestamp))

    @property
    def wait_seconds(self):
        if self.remaining is None:
            return 0
        current_time = self._current_utctime()
        time_to_reset = self.reset_timestamp - current_time
        if time_to_reset < timedelta(0):
            return 0
        return (time_to_reset / self.remaining).total_seconds()

    def process_response(self, response):
        self.record_rate_limit(
            remaining=response.headers['X-RateLimit-Remaining'],
            reset_timestamp=response.headers['X-RateLimit-Reset'],
        )

    def wait_before_request(self):
        click.echo(" r: {self.remaining}, ws: {self.wait_seconds}".format(self=self))

        self._do_sleep(self.wait_seconds)
