from __future__ import print_function
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

'''
Notes and references:
1. acknowl: answer for using service account. https://stackoverflow.com/questions/64570647/google-drive-api-python-service-account-example
2. scopes: https://developers.google.com/identity/protocols/oauth2/scopes
3. service account info: https://developers.google.com/identity/protocols/oauth2/service-account#httprest_1
4. quickstart ref that follows on from answer in 1: https://developers.google.com/drive/api/v3/quickstart/python
'''

import os.path

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
KEY_FILE_LOCATION = 'credentials.json'


def initialize_drive():
    """Initializes an service object.

    Returns:
        An authorized service object.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

initialize_drive()