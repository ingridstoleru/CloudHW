import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


os.environ['DEBUG'] = '1'
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = flask.Flask(__name__)
app.debug = True
app.secret_key = 'secret_key'

@app.route('/')
def index():
    return print_index()


@app.route('/list')
def list_files_drive():
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    files = drive.files().list(pageSize=10,fields="nextPageToken, files(id, name)").execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**files)

@app.route('/metadata/<fileID>')
def print_file_metadata(fileID):
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    file = drive.files().get(fileId=fileID).execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**file)

@app.route('/content/<fileID>')
def print_file_content(fileID):
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    file = drive.files().get_media(fileId=fileID).execute()

    flask.session['credentials'] = credentials_to_dict(credentials)
    return file

@app.route('/import/<fileID>')
def import_file(fileID):
    if 'credentials' not in flask.session:
      return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    file = drive.files().get_media(fileId=fileID).execute()

    flask.session['credentials'] = credentials_to_dict(credentials)
    return file

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('auth', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/auth')
def auth():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('auth', _external=True)

    authorization_response = flask.request.url.replace('http', 'https')
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('list_files_drive'))


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' + print_index())


def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index():
    return ('<table>' +
          '<tr><td><a href="/list">List</a></td>' +
          '<td>&nbsp;&nbsp;&nbsp;&nbsp;Listeaza toate fisierele din Drive ' +
          '    </td></tr>' +
          '<tr><td>/import/fileID</td>' +
          '<td>&nbsp;&nbsp;&nbsp;&nbsp;Importa un fisier din drive' +
          '    </td></tr>' +
          '<tr><td>/metadata/fileID</td>' +
          '<td>&nbsp;&nbsp;&nbsp;&nbsp;Afiseaza metadatele unui fisier din drive' +
          '    </td></tr>' +
          '<tr><td>/content/fileID</td>' +
          '<td>&nbsp;&nbsp;&nbsp;&nbsp;Afiseaza continutul unui fisier din drive' +
          '    </td></tr>')
          #'<tr><td><a href="/clear">Sterge credentialele</a></td>' +
          #'<td></td></tr></table>')


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8009, debug=True)