from __future__ import print_function
import json
from pathlib import Path
import time
import pandas as pd
import os.path
import shutil
import os


from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.file']
KEY_FILE_LOCATION = 'credentials.json'

creds = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)
service = build('drive', 'v3', credentials=creds)
count=0

directory = "C:\\Users\\sjwu1\\Journal_Data"
temp = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\Master lists\\AER_master.xlsx")
temp2 = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\pivots\\AER_pivots.xlsx")
folder_ID = "1DJ0Ph_-JWSvkzzI70EVCU9JRb1jMp_cO"
file_type="json"
#src_folder = r"C:\Users\sjwu1\Journal_Data\\Scihub"
#dst_folder = r"C:\Users\sjwu1\Journal_Data\\Scihub_checked"

total=0
total_uploaded=0
total_session=0
fulllist_s_1940=0
for ind in temp2.index:
    temp3=temp[temp['issue_url']==temp2['issue_url'][ind]]
    downloaded=0
    uploaded = 0
    session_uploaded=0
    for ind2 in temp3.index:
        file_name=temp['stable_url'][ind2].split('/')[-1]+"."+file_type
        if (temp2['year'][ind]==1983):
            fulllist_s_1940+=1
            #print(file_name+" "+str(os.path.isfile(directory+file_name)))
            upload_indicator=1 #defaults to upload - we can handle duplicates
            try:
                page_token = None
                while True:
                    # Call the Drive v3 API
                    # "mimeType = 'application/vnd.google-apps.folder'" # files that are folders
                    # "name ='354.pdf'" #search by name
                    response = service.files().list(q="name ='"+file_name+"'",
                        fields="nextPageToken, files(id,name)",
                        pageToken=page_token).execute()
                    items = response.get('files', [])                
                    if (len(items)>0):
                        uploaded+=1
                        #service.files().delete(fileId=items[0]['id']).execute()
                        #print(u'already uploaded: {0} ({1})'.format(items[0]['name'], items[0]['id']))
                        upload_indicator=0
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                    print(count)
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f'An error occurred: {error}')
            if(os.path.isfile(directory+"\\"+file_name)):
                downloaded+=1
                if (upload_indicator==1):
                    try:
                        file_metadata = {'name': file_name, 'parents': [folder_ID]}
                        media = MediaFileUpload(directory+"\\"+file_name, mimetype='application/'+file_type, resumable=True)
                        file = service.files().create(body=file_metadata,
                                                            media_body=media,
                                                            fields='id').execute()
                        print ('File uploaded this session: '+ file_name+' ('+file.get('id')+')')
                        uploaded+=1
                        session_uploaded+=1
                    except Exception as e:
                        print(e)
                #source = directory + "\\"+ file_name
                #destination = dst_folder +"\\"+ file_name
                #shutil.move(source,destination)
    total_session+=session_uploaded
    total_uploaded+=uploaded
    total=total+downloaded
    print(str(temp2['year'][ind])+" no. docs: "+str(temp2['no_docs'][ind])+" Issue URL: "+str(temp2['issue_url'][ind])+" In dir: "+str(downloaded)+ " On Drive: "+str(uploaded) +" Session upload: "+str(session_uploaded))

print('\n')
print('total downloaded in directory: ' + str(total))
print('total uploaded this session: ' + str(total_session))
print('total on google drive: '+str(total_uploaded))
print('total papers after 1940: '+str(fulllist_s_1940))
