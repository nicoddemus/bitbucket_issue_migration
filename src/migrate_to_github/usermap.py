import click
import attr
import collections


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




@attr.s
class UserMap(object):
    map = attr.ib(validators=attr.validators.instance_of(collections.MutableMapping))

    def add_from(self, source):
        refresh_usermap(
                source=source, target=self.map, union=True)

    def refresh_on(self, target):
        refresh_usermap(
                source=self.map, target=target, union=False)

    @classmethod
    def sync_all(cls, mappings):
        merged = cls()
        for user_map in mappings:
            merged.add_from(user_map)
        for user_map in mappings:
            merged.refresh_on(user_map)
