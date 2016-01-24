import click
from pathlib2 import Path

from migrate_to_github.cli import commands
from migrate_to_github.cli.commands import upload_github_issues
from migrate_to_github.store import FileStore


@click.group(chain=True)
@click.pass_context
@click.argument('target', type=Path)
def main(ctx, target):
    ctx.obj = FileStore(path=target)


def command(func):
    return main.command()(click.pass_obj(func))


@command
@click.argument('bitbucket')
@click.argument('github')
def init(target, bitbucket, github):
    commands.init(path=target.path, github=github, bitbucket=bitbucket)


@command
def fetch(store):
    commands.fetch(store)


@command
def extract_users(store):
    commands.extract_users(store)


@command
def convert(store):
    commands.convert(store)


@command
@click.option('--token', envvar='GITHUB_TOKEN')
def upload(store, token):
    upload_github_issues(store, token)
