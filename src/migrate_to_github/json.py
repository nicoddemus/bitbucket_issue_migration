import json


NOT_GIVEN = object()


def dump(data, path):
    with path.open('w') as fp:
        json.dump(data, fp, sort_keys=True, indent=2)


def load(path, default=NOT_GIVEN):
    try:
        fp = path.open()
    except IOError:
        if default is not NOT_GIVEN:
            return default
        raise
    else:
        with fp:
            return json.load(fp)
