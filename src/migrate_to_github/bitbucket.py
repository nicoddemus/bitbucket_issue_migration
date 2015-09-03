import operator

from .util import MiniClient
from .formating import format_user

ISSUES_API = "https://api.bitbucket.org/1.0/repositories/{repo}/issues"


def get_client(repo):
    """
    :param repo: bitbucket repository as {name}/{repo} string
    """
    return MiniClient(ISSUES_API.format(repo=repo))


def iter_issues(client, start_id):
    while True:
        url = '/?start_id={start_id}'.format(start_id=start_id)
        result = client.get(url)
        if not result['issues']:
            break
        start_id += len(result['issues'])
        print (start_id)
        for item in result['issues']:
            yield item


def get_comments(client, issue_id):
    url = "/{id}/comments/".format(id=issue_id)
    result = client.get(url)
    by_creation_date = operator.itemgetter("utc_created_on")
    ordered = sorted(result, key=by_creation_date)
    filtered = filter(operator.itemgetter('content'), ordered)
    list(map(_parse_comment, filtered))


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
