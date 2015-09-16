from pathlib import Path
import click
from . import util
from . import bitbucket


@click.group(chain=True)
@click.pass_context
def main(ctx):
    ctx.obj = target = Path('issues')
    if not target.is_dir():
        target.mkdir(parents=True)


@main.command()
@click.pass_obj
@click.argument('bitbucket_repo')
def fetch_issues(target, bitbucket_repo):
    get = util.Getter(bitbucket.REPO_API, repo=bitbucket_repo)
    issues = bitbucket.iter_issues(get)
    with click.progressbar(issues,
                           length=len(issues),
                           show_pos=True,
                           show_percent=True,
                           label="Fetching Issues") as bar:
        for issue in bar:
            util.dump(
                issue, target,
                'bb_{id:05d}.json', id=issue['local_id'])


@main.command()
@click.pass_obj
@click.argument('bitbucket_repo')
def simplify_bitbucket_issues(target, bitbucket_repo):
    items = list(target.glob('bb_*.json'))
    with util.progress(items, label='Preparing Github Import Requests') as bar:
        for issue in bar:
            data = util.load(issue)
            simplified = bitbucket.simplify_issue(data, repo=bitbucket_repo)
            util.dump(
                simplified, target,
                'simple_{name}', name=issue.name)


@main.command()
@click.pass_obj
@click.argument('github_repo')
@click.option('--token', envvar='GITHUB_TOKEN')
def upload_issues(target, github_repo, token):
    post = util.Poster(token, util.GITHUB_REPO_IMPORT_API, repo=github_repo)
    items = list(target.glob('simple_bb_*.json'))
    with util.progress(items, label='Uploading Github Import Requests') as bar:
        for issue in bar:
            with issue.open() as fp:
                post(fp.read())
