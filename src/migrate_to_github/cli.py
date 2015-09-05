from pathlib import Path
import attr
import click
from . import json
from . import bitbucket


@attr.s
class Config(object):
    root = attr.ib()

    def __getattr__(self, key):
        return json.load(self._path, {})[key]

    @property
    def _path(self):
        return self.root.joinpath('migrate_to_github.json')

    def _write(self, data):
        json.dump(data, self._path)

    def update(self, **changes):
        data = json.load(self._path, {})
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
        target.mkdir(parents=True)
    client = bitbucket.get_client(config.bitbucket_repo)
    issues = bitbucket.iter_issues(client)
    with click.progressbar(issues,
                           length=len(issues),
                           show_pos=True,
                           show_percent=True,
                           label="Fetching Issues") as bar:
        for issue in bar:
            json.dump(
                issue,
                target.joinpath('{local_id:05d}.json'.format(**issue)))


@main.command()
@click.pass_obj
def simplify_bitbucket_issues(config):
    source = config.root.joinpath('issues/from_bitbucket')
    target = config.root.joinpath('issues/simpe_bitbucket')
    if not target.is_dir():
        target.mkdir(parents=True)
    for issue in source.glob('*.json'):
        data = json.load(issue)
        simplified = bitbucket.simplify_issue(
            data, repo=config.bitbucket_repo)
        json.dump(simplified, target.joinpath(issue.name))
