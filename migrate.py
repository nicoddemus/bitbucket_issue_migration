#!/usr/bin/env python
#-*- coding: utf-8 -*-

# This file is part of the bitbucket issue migration script.
#
# The script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the bitbucket issue migration script.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import click
import operator
import requests


class MiniClient(object):
    def __init__(self, base_url, session=None):
        self.session = session or requests.Session()
        self.base_url = base_url

    @classmethod
    def with_token(cls, base_url, api_token):
        session = requests.Session()
        session.headers.update({
            'Authorization': 'token ' + api_token
        })
        return cls(base_url=base_url, session=session)

    def get(self, url):
        return self.session.get(self.base_url + url).json()


@click.command(help=(
    "A tool to migrate issues from Bitbucket to GitHub.\n"
    "note: the Bitbucket repository and issue tracker have to be"
    "public"
))
@click.argument('bitbucket_repo')
@click.argument('github_repo')
@click.option('--start-id', default=0, type=int)
@click.option('--create', is_flag=True)
@click.option('--dry-run', is_flag=True)
@click.option('--api-token', metavar='api_token',
              envvar="GITHUB_API_TOKEN", type=str)
def migrate(bitbucket_repo, create, github_repo, api_token, dry_run, start_id):
    bb = MiniClient(
        "https://api.bitbucket.org/1.0/repositories/" +
        bitbucket_repo + '/issues')
    issues = iter_issues(bb, start_id)
    # gh = MiniClient()
    for issue in issues:
        issue.pop('content')
        click.echo(issue)


def iter_issues(bb, start_id):
    while True:
        url = '/?start_id={start_id}'.format(start_id=start_id)
        result = bb.get(url)
        if not result['issues']:
            break
        start_id += len(result['issues'])
        print (start_id)
        for item in result['issues']:
            yield item


# Formatters
def format_user(author_info):
    if not author_info:
        return "Anonymous"

    if author_info['first_name'] and author_info['last_name']:
        return " ".join([author_info['first_name'], author_info['last_name']])

    if 'username' in author_info:
        return '[{0}](http://bitbucket.org/{0})'.format(
            author_info['username']
        )


def format_name(issue):
    return format_user(issue.get('reported_by'))


def format_body(options, issue):
    content = clean_body(issue['content'])
    return """{}


- Bitbucket: https://bitbucket.org/{}/issue/{}
- Originally reported by: {}
- Originally created at: {}
""".format(
        content,
        options.bitbucket_repo,
        issue['local_id'],
        format_name(issue),
        issue['created_on']
    )


def format_comment(comment):
    return """Original comment by {user}

{body}""".format(**commemt)


def clean_body(body):
    lines = []
    in_block = False
    for line in text_type(body).splitlines():
        if line.startswith("{{{") or line.startswith("}}}"):
            if "{{{" in line:
                before, part, after = line.partition("{{{")
                lines.append('    ' + after)
                in_block = True

            if "}}}" in line:
                before, part, after = line.partition("}}}")
                lines.append('    ' + before)
                in_block = False
        else:
            if in_block:
                lines.append("    " + line)
            else:
                lines.append(line.replace("{{{", "`").replace("}}}", "`"))
    return "\n".join(lines)


def get_comments(bb, issue):
    '''
    Fetch the comments for a Bitbucket issue
    '''
    url = "/{local_id}/comments/".format(**issue)
    result = bb.get(url).json()
    by_creation_date = operator.itemgetter("utc_created_on")
    ordered = sorted(result, key=by_creation_date)
    # filter only those that have content; status comments (assigned,
    # version, etc.) have no body
    filtered = filter(operator.itemgetter('content'), ordered)
    return list(map(_parse_comment, filtered))


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


class SubmitHandler():


    def handle(self, issue):
        comments = get_comments(issue)
        body = format_body(self.options, issue)
        self.push_issue(issue, body, comments)

    def push_issue(self, issue, body, comments):
        # Create the issue
        repo_path = self.options.github_repo
        issue_data = {
            'title': issue['title'],
            'body': body
        }
        repo = self.github.get_repo(repo_path)
        new_issue = repo.create_issue(**issue_data)

        # Set the status and labels
        if issue['status'] == 'resolved':
            new_issue.edit(state='closed')

        # Everything else is done with labels in github
        elif issue['status'] == 'wontfix':
            new_issue.edit(state='closed')
        elif issue['status'] == 'on hold':
            pass
        elif issue['status'] == 'invalid':
            new_issue.edit(state='closed')
        elif issue['status'] == 'duplicate':
            new_issue.edit(state='closed')

        # Milestones

        # Add the comments
        for comment in comments:
            new_issue.create_comment(format_comment(comment))

        print("Created: {} [{} comments]".format(
            issue['title'], len(comments)
        ))


if __name__ == "__main__":
    migrate()
