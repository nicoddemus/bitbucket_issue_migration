from __future__ import print_function
import operator

from .util import MiniClient
from .formating import format_name, format_user

REPO_API = "https://api.bitbucket.org/1.0/repositories/{repo}"


def get_client(repo):
    """
    :param repo: bitbucket repository as {name}/{repo} string
    """
    return MiniClient(REPO_API.format(repo=repo))


def iter_issues(client):
    start_id = 0

    while True:
        print('start', start_id)
        url = '/issues/?start={start_id}'.format(start_id=start_id)
        result = client.get(url)
        if not result['issues']:
            break
        start_id += len(result['issues'])
        for item in result['issues']:
            yield item


def simple_issue(issue):
    return {
        'id': issue['local_id'],
        'status': issue['status'],
        'content': issue['content'],
        'title': issue['title'],
        'reported_user': format_name(issue),
        'utc_last_updated': issue['utc_last_updated'],
    }


def get_comments(client, issue_id):
    url = "/issues/{id}/comments/".format(id=issue_id)
    return client.get(url)


def _parse_comment(comment):
    """
    Parse a comment as returned from Bitbucket API.
    """
    return dict(
        user=format_user(comment['author_info']),
        created_at=comment['utc_created_on'],
        body=comment['content'],
        number=comment['comment_id'],
    )
