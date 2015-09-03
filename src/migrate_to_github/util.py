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
