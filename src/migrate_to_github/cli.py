from pathlib2 import Path
import click
from . import utils
from . import bitbucket


from .utils import gprocess
from .store import FileStore


@click.group(chain=True)
@click.pass_context
@click.argument('target', type=Path)
def migrate_tool(ctx, target):
    ctx.obj = FileStore(path=target)


@migrate_tool.command()
@click.pass_obj
@click.argument('bitbucket')
@click.argument('github')
def init(store, bitbucket, github):
    store.path.mkdir(parents=True, exist_ok=True)
    store['repos'] = {
        'bitbucket': bitbucket,
        'github': github
    }


@migrate_tool.command()
@click.pass_obj
def fetch(store):
    issues, comments = bitbucket.stores(store)
    get = bitbucket.get_getter(store)
    current_issues = bitbucket.iter_issues(get)
    for elem in utils.gprocess(current_issues, label="Fetching Issues"):
        eid = elem['local_id']
        issues[eid] = elem
        comments[eid] = bitbucket.get_comments(get, elem)


@migrate_tool.command()
@click.pass_obj
def extract_users(store):
    """extract username list from authormap"""

    issues, comments = bitbucket.stores(store)

    usermap = store.get('users', {})
    for item in gprocess(issues,
                         label='Extracting usermap',
                         show_pos=False, show_percent=False):
        issue = issues[item]
        comment_list = comments[item]

        authors = utils.contributors(issue, comment_list)

        for author in authors:
            if author not in usermap:
                usermap[author] = None
        store['users'] = usermap


@migrate_tool.command()
@click.pass_obj
def convert(store):
    issues, comments = bitbucket.stores(store)

    simple_store = FileStore.ensure(store.path / 'github_uploads')

    repo = store['repos']['bitbucket']
    items = issues.items()
    for key, issue in gprocess(items, label='Preparing Import Requests'):
        issue['comments'] = comments[key]
        simplified = bitbucket.simplify_issue(issue, comments, repo=repo)
        simple_store[key] = simplified


@migrate_tool.command()
@click.pass_obj
@click.argument('github_repo')
@click.option('--token', envvar='GITHUB_TOKEN')
def upload(store, github_repo, token):
    post = utils.Poster(token, utils.GITHUB_REPO_IMPORT_API, repo=github_repo)
    simple_store = FileStore.ensure(store.path / 'github_uploads')
    for issue in gprocess(simple_store, label='Uploading Import Requests'):
        post(simple_store.raw_data(issue))
