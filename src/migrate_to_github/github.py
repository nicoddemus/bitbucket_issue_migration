from .util import MiniClient

REPO_API = 'https://api.github.com/repos/{repo}/import/issues'


def get_client(repo, token):
    return MiniClient.with_token(
        REPO_API.format(repo=repo), token
    )
