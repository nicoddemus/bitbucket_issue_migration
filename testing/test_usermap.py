import pytest
from click.testing import CliRunner
from migrate_to_github.cli.usermap import main, refresh_usermap
from migrate_to_github.utils import dump, load


def die(m, **kw):
    raise ValueError(m, kw)


def test_usermap_sync(tmppath):

    dump({'test': None}, tmppath/'a.json')

    dump({'test': 'a', 'bad': 'b'}, tmppath/'b.json')

    runner = CliRunner()
    result = runner.invoke(main, [
        str(tmppath/'a.json'),
        str(tmppath/'b.json'),
    ], catch_exceptions=False)
    assert result.exit_code == 0

    assert load(tmppath/'a.json') == {'test': 'a'}


@pytest.mark.parametrize('source, target, union, expected', [
    ({}, {}, True, {}),
    ({'a': '1'}, {}, True, {'a': '1'}),
    ({'a': '1'}, {'a': None}, False, {'a': '1'}),
    ({'a': '1'}, {}, False, {}),
])
def test_refresh_usermap(source, target, union, expected):
    target = target.copy()
    refresh_usermap(
        source=source, target=target, union=union, _warn=die)
    assert target == expected


def test_refresh_usermap_warning():

    def assert_warn(msg, key, value, targetvalue):
        assert key == 'a'
        assert value == '1'
        assert targetvalue == '2'
    target = {'a': 'b'}
    refresh_usermap(
        source={'a': '1'},
        target=target,
        union=False)
    assert target == {'a': 'b'}
