

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

{body}""".format(**comment)


def clean_body(body):
    lines = []
    in_block = False
    for line in body.splitlines():
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
