from __future__ import print_function
#from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

'''
Notes and references:
This file is necessary for reference as the python notes on drive api are outdates for python. Eg: print statement is incorrect.

1. acknowl: answer for using service account. https://stackoverflow.com/questions/64570647/google-drive-api-python-service-account-example
2. quickstart ref that follows on from answer in 1: https://developers.google.com/drive/api/v3/quickstart/python
3. scopes: https://developers.google.com/identity/protocols/oauth2/scopes

To read:
1. service account info: https://developers.google.com/identity/protocols/oauth2/service-account#httprest_1
2. service account info: https://cloud.google.com/iam/docs/impersonating-service-accounts#iam-service-accounts-grant-role-sa-rest

Todo:
1. Research how to restrict access of service accounts to readonly and post only, no modify or delete.
2. Research why some folders with viewer access allow uploads (FR drive) and owner drive does not for viewer only folders.
'''

import os.path

SCOPES = ['https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.file']
KEY_FILE_LOCATION = 'credentials.json'


def initialize_drive():
    """Initializes an service object. Does some arbitrary checks

    Returns:
        An authorized service object. Or not. Depends on the mood.
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)
    count=0
    try:
        service = build('drive', 'v3', credentials=creds)
        page_token = None
        while True:
            # Call the Drive v3 API
            # "mimeType = 'application/vnd.google-apps.folder'" # files that are folders
            # "name ='354.pdf'" #search by name
            response = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token).execute()
            items = response.get('files', [])
            
            if not items:
                print('No files found.')
                return
            
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                count+=1
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        print(str(count)+ ' files/folders found')
        

        # Uploading a file

        # this is the folder id for the destination folder on google drive
        # it is set manually to a folder called Crowd Sourcing
        folder_id = "1UCcp9d5zuXami-LGi7v5H8v7DJGI8xZA"
        
        file_metadata = {
            "name": "1881665.pdf",
            "parents": [folder_id]
            }
        # first argument is path to pdf on local
        media = MediaFileUpload("1881665.pdf", mimetype="application/pdf")
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields="id").execute()
        print("File ID: "+ file.get("id"))    
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

initialize_drive()