import click


def warn(message, **kwargs):
    click.secho(message.format(**kwargs), fg='yellow', bold=True)


def refresh_usermap(source, target, union=False, _warn=warn):
    for key, value in source.items():
        if value is None:
            continue

        targetvalue = target.get(key)
        if targetvalue is not None and value != targetvalue:
            _warn('for {key} the {targetvalue} !0 {value}',
                  key=key, targetvalue=targetvalue, value=value)
            continue
        if key in target or union:
            target[key] = value


def bitbucket_userlink(name):
    return '[{name}@bitbucket](https://bitbucket.org/{name})'


def nametext(map, name):
    new = map.get(name)

    if new:
        return '@' + (name if new is True else new)
    else:
        return bitbucket_userlink(name)


def sync_all(mappings):
    merged = {}
    for user_map in mappings:
        refresh_usermap(source=user_map, target=merged, union=True)
    for user_map in mappings:
        refresh_usermap(source=merged, target=user_map, union=False)
