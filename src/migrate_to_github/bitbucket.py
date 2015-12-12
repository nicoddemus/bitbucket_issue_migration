from __future__ import print_function
from .formating import format_user, format_comment
from .utils import Getter


REPO_API = "https://api.bitbucket.org/1.0/repositories/{repo}"


class iter_issues(object):
    def __init__(self, get):
        self.get = get
        self._pop = None
        self._real_iter = None
        self._count = None

    def __iter__(self):
        return self

    def __len__(self):
        if self._count is None:
            assert self._pop is None
            self._pop = next(self)
        return self._count

    def __next__(self):
        if self._real_iter is None:
            self._real_iter = fetch_issues(self, self.get)
        if self._pop is None:
            return next(self._real_iter)
        else:
            result, self._pop = self._pop, None
            return result


def fetch_issues(_iter, get):
    start_id = 0
    while True:
        issue_url = '/issues/?start={start_id}'.format(start_id=start_id)
        result = get(issue_url)
        _iter._count = result['count']
        if not result['issues']:
            break
        start_id += len(result['issues'])
        for item in result['issues']:
            comment_url = '/issues/{id}/comments/'.format(id=item['local_id'])
            item['comments'] = get(comment_url)
            yield item


def simplify_issue(bb_issue, repo):
    simplified = {}
    issue = simplified['issue'] = {}
    issue['title'] = bb_issue['title']
    from .formating import format_body
    issue['body'] = format_body(bb_issue, repo)
    if bb_issue['status'] in 'closed wontfix resolved':
        issue['closed'] = True
    simplified['comments'] = [
        {'body': format_comment(_parse_comment(x))}
        for x in bb_issue['comments']
    ]
    return simplified


def _parse_comment(comment):
    """
    Parse a comment as returned from Bitbucket API.
    """
    return dict(
        user=format_user(comment['author_info']),
        created_at=comment['utc_created_on'],
        body=comment['content'],
        number=comment['comment_id'], )


def get_issues(repo):
    get = Getter(REPO_API, repo=repo)
    return iter_issues(get)
