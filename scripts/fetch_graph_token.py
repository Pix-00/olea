import sys
import uuid
from pathlib import Path

import msal
from flask import Flask, jsonify, redirect, request, url_for

app = Flask(__name__)

AUTHORITY = 'https://login.microsoftonline.com/common'
SCOPES = ['Files.ReadWrite.All']

state = str(uuid.uuid4())


@app.route('/')
def login():
    msal_app = _build_msal_app()
    auth_url = msal_app.get_authorization_request_url(scopes=SCOPES,
                                                      state=state,
                                                      redirect_uri=url_for('authorized',
                                                                           _external=True))
    return redirect(auth_url)


@app.route('/done')
def done():
    return 'successfully logged in'


@app.route('/getToken')
def authorized():
    if request.args.get('state') != state:
        return redirect(url_for('login'))

    if 'error' in request.args:  # Authentication/Authorization failure
        return jsonify(request.args)

    if request.args.get('code'):
        cache = msal.SerializableTokenCache()

        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=SCOPES,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for('authorized', _external=True))

        if 'error' in result:
            return jsonify(request.args)

        with TOKEN_PATH.open('w') as f:
            f.write(cache.serialize())

    return redirect(url_for('done'))


def _build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(CLIENT_ID,
                                              authority=AUTHORITY,
                                              client_credential=CLIENT_SECRET,
                                              token_cache=cache)


if __name__ == '__main__':
    DIR = Path(__file__).parents[1]
    sys.path.append(str(DIR))

    from configs import load_config

    config = load_config()

    data_dir: Path = config['ONEDRIVE_DATA_DIR']
    data_dir.mkdir(exist_ok=True)

    TOKEN_PATH = data_dir / 'token.json'
    CLIENT_ID = config['ONEDRIVE_CLIENT_ID']
    CLIENT_SECRET = config['ONEDRIVE_CLIENT_SECRET']

    app.run()
