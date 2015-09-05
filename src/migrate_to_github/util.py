import requests
import click
import json

class MiniClient(object):
    def __init__(self, base_url, session=None):
        self.session = session or requests.Session()
        self.base_url = base_url

    @classmethod
    def with_token(cls, base_url, api_token):
        session = requests.Session()
        session.headers.update({
            'Authorization': 'token ' + api_token,
            'Accept': 'application/vnd.github.golden-comet-preview+json',

        })
        return cls(base_url=base_url, session=session)

    def get(self, url):
        return self.session.get(self.base_url + url).json()

    def post(self, url, data):
        response = self.session.post(self.base_url + url, data=data)
        if response.status_code in (200, 202):
            return response.json()
        else:
            click.echo(response.status_code)
            click.echo(json.dumps(
                dict(response.headers), indent=2, sort_keys=True))
            click.echo(json.dumps(response.json(), indent=2, sort_keys=True))
            raise SystemExit()
