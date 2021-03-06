__all__ = ['Graph']

import json
from functools import wraps

import msal
import requests

from .token_cache import TokenCache

AUTHORITY = "https://login.microsoftonline.com/common"
ENDPOINT = 'https://graph.microsoft.com/v1.0/'


def handle_error(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        r = f(*args, **kwargs)

        if not r.ok:
            print('- - - - Req Content - - - -')
            print(r.content)
            raise Exception(f'Unexceptd HTTP Error: {r.status_code}')

        if 'application/json' in r.headers.get('content-type', '').split(';'):
            return r.json()

        return r

    return decorated


class Graph():
    def __init__(self, config):
        client_id = config['client_id']
        secret = config['client_secret']
        authority = config.get('authority', AUTHORITY)
        self.endpoint = config.get('endpoint', ENDPOINT)
        self.scopes = ['Files.ReadWrite.All']

        self.token_cache = TokenCache(path=config['data_dir'])
        self.cca = msal.ConfidentialClientApplication(client_id,
                                                      authority=authority,
                                                      client_credential=secret,
                                                      token_cache=self.token_cache.cache)

        self.account = self.cca.get_accounts()[0]

    @property
    def token(self):
        r = self._get_token()
        return f'Bearer {r["access_token"]}'

    def _get_token(self, force_refresh=False):
        r = self.cca.acquire_token_silent_with_error(self.scopes,
                                                     account=self.account,
                                                     force_refresh=force_refresh)
        if 'error' in r:
            raise Exception(json.dumps(r['error']))

        self.token_cache.save()
        return r

    @handle_error
    def get(self, req: str):
        return requests.get(
            url=f'{self.endpoint}{req}',
            headers={'Authorization': self.token},
        )

    @handle_error
    def post(self, req: str, data: dict):
        return requests.post(
            url=f'{self.endpoint}{req}',
            headers={'Authorization': self.token},
            json=data,
        )

    @handle_error
    def delete(self, req: str):
        return requests.delete(
            url=f'{self.endpoint}{req}',
            headers={'Authorization': self.token},
        )
