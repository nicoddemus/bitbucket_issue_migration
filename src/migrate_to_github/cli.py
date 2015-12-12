from pathlib import Path
import click
from . import utils
from . import bitbucket


from .utils import gprogress, dump


@click.group(chain=True)
@click.pass_context
@click.option('--target', default='issues', type=Path)
def main(ctx, target):
    ctx.obj = target
    if not target.is_dir():
        target.mkdir(parents=True)


@main.command()
@click.pass_obj
@click.argument('repo')
def fetch_issues(target, repo):
    issues = bitbucket.get_issues(repo)
    utils.dump({'repo': repo}, target, utils.BB_METADATA)
    for issue in utils.gprogress(issues, label="Fetching Issues"):
        dump(issue, target, 'bb_{id:05d}.json', id=issue['local_id'])


@main.command()
@click.pass_obj
def simplify_bitbucket_issues(target):
    repo = utils.load(target / utils.BB_METADATA)['repo']
    items = list(target.glob('bb_*.json'))
    for issue in gprogress(items, label='Preparing Github Import Requests'):
        data = utils.load(issue)
        simplified = bitbucket.simplify_issue(data, repo=repo)
        dump(
            simplified, target,
            'simple_{name}', name=issue.name)


@main.command()
@click.pass_obj
@click.argument('github_repo')
@click.option('--token', envvar='GITHUB_TOKEN')
def upload_issues(target, github_repo, token):
    post = utils.Poster(token, utils.GITHUB_REPO_IMPORT_API, repo=github_repo)
    items = list(target.glob('simple_bb_*.json'))
    for issue in gprogress(items, label='Uploading Github Import Requests'):
        with issue.open() as fp:
            post(fp.read())
