from pathlib import Path
import click
from . import json
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
    client = bitbucket.get_client(bitbucket_repo)
    issues = bitbucket.iter_issues(client)
    with click.progressbar(issues,
                           length=len(issues),
                           show_pos=True,
                           show_percent=True,
                           label="Fetching Issues") as bar:
        for issue in bar:
            json.dump(
                issue,
                target.joinpath('bb_{local_id:05d}.json'.format(**issue)))


@main.command()
@click.pass_obj
@click.argument('bitbucket_repo')
def simplify_bitbucket_issues(target, bitbucket_repo):
    items = list(target.glob('bb_*.json'))
    with click.progressbar(
            items, show_pos=True, show_percent=True,
            label='Preparing Github Import Requests') as bar:
        for issue in bar:
            data = json.load(issue)
            simplified = bitbucket.simplify_issue(data, repo=bitbucket_repo)
            json.dump(simplified, target.joinpath('simple_' + issue.name))


@main.command()
@click.pass_obj
@click.argument('github_repo')
@click.option('--token', envvar='GITHUB_TOKEN')
def upload_issues(target, github_repo, token):
    from . import github
    items = list(target.glob('simple_bb_*.json'))
    client = github.get_client(github_repo, token)
    with click.progressbar(
            items, show_pos=True, show_percent=True,
            label='Uploading Github Import Requests') as bar:
        for issue in bar:
            with issue.open() as fp:
                client.post('', fp.read())
