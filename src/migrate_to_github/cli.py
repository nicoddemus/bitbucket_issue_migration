from pathlib import Path
import json
import attr
import click

from . import bitbucket


@attr.s
class Config(object):
    root = attr.ib()

    def __getattr__(self, key):
        return self._read()[key]

    @property
    def _path(self):
        return self.root.joinpath('migrate_to_github.json')

    def _read(self):
        try:
            fp = self._path.open()
        except IOError:
            return {}
        else:
            with fp:
                return json.load(fp)

    def _write(self, data):
        with self._path.open('w') as fp:
            json.dump(data, fp, sort_keys=True, indent=2)

    def update(self, **changes):
        data = self._read()
        data.update(changes)
        self._write(data)


@click.group()
@click.pass_context
@click.option('--path', type=click.Path(), default='.')
def main(ctx, path):
    ctx.obj = Config(Path(path))


@main.command()
@click.pass_obj
@click.argument('kv', nargs=-1)
def configure(config, kv):
    config.update(dict(x.split('=', 1) for x in kv))


@main.command()
@click.pass_obj
@click.argument('repo')
def init_bitbucket(config, repo):
    config.update(bitbucket_repo=repo)


@main.command()
@click.pass_obj
def fetch_issues(config):
    target = config.root.joinpath('issues/from_bitbucket')
    if not target.is_dir():
        target.mkdir()
    client = bitbucket.get_client(config.bitbucket_repo)
    issues = bitbucket.iter_issues(client)
    for issue in issues:
        issue['comments'] = bitbucket.get_comments(client, issue['local_id'])
        with target.joinpath(
                '{local_id:05d}.json'.format(**issue)).open('w') as fp:
            json.dump(issue, fp, sort_keys=True, indent=2)
