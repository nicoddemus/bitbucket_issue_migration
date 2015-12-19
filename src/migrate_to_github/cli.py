from pathlib2 import Path
import click
from . import utils
from . import bitbucket


from .utils import gprocess, dump


@click.group(chain=True)
@click.pass_context
@click.argument('target', type=Path)
def main(ctx, target):
    ctx.obj = target


@main.command()
@click.pass_obj
@click.argument('repo')
def init(target, repo):
    target.mkdir(parents=True, exist_ok=True)
    dump({'repo': repo}, target / utils.BB_METADATA)


@main.command()
@click.pass_obj
def fetch(target):
    repo = utils.load(target / utils.BB_METADATA)['repo']
    issue_folder = target / 'bb_issues'
    issue_folder.mkdir(parents=True, exist_ok=True)

    issues = bitbucket.get_issues(repo)
    for elem in utils.gprocess(issues, label="Fetching Issues"):
        if elem.issue:
            dump(
                elem.issue,
                issue_folder / 'bb_{elem.id:05d}_issue.json'.format(elem=elem))
            if elem.comments:
                dump(
                    elem.issue,
                    issue_folder / 'bb_{elem.id:05d}_comments.json'.format(elem=elem))



@main.command()
@click.pass_obj
def extract_users(target):
    '''extract username list from authormap'''
    issue_folder = target / 'bb_issues'
    items = list(issue_folder.glob('bb_*.json'))

    usermap = utils.load(target / utils.USERMAP, default={})
    for issue in gprocess(items, label='Preparing Github Import Requests'):
        data = utils.load(issue)

        authors = utils.contributors(data)
        for author in authors:
            if authors not in usermap:
                usermap[author] = None
        utils.dump(usermap, target / utils.USERMAP)


@main.command()
@click.pass_obj
@click.argument('userlist', type=Path)
def take_users(target, userlist):
    usermap = utils.load(target / utils.USERMAP)
    new = utils.load(userlist)
    for name, value in new.items():
        if name in usermap and value is not None:
            usermap[name] = value

@main.command()
@click.pass_obj
def simplify_bitbucket_issues(target):
    repo = utils.load(target / utils.BB_METADATA)['repo']
    items = list(target.glob('bb_*.json'))
    for issue in gprocess(items, label='Preparing Github Import Requests'):
        data = utils.load(issue)
        simplified = bitbucket.simplify_issue(data, repo=repo)
        dump(
            simplified,
            target / ('simple_' + issue.name))


@main.command()
@click.pass_obj
@click.argument('github_repo')
@click.option('--token', envvar='GITHUB_TOKEN')
def upload_issues(target, github_repo, token):
    post = utils.Poster(token, utils.GITHUB_REPO_IMPORT_API, repo=github_repo)
    items = list(target.glob('simple_bb_*.json'))
    for issue in gprocess(items, label='Uploading Github Import Requests'):
        with issue.open() as fp:
            post(fp.read())
