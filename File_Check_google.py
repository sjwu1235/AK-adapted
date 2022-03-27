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

directory = "C:\\Users\\sjwu1\\Journal_Data\\test"
temp = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\Master lists\\AER_master.xlsx")
temp2 = pd.read_excel("C:\\Users\\sjwu1\\Journal_Data\\pivots\\AER_pivots.xlsx")

#src_folder = r"C:\Users\sjwu1\Journal_Data\\Scihub"
#dst_folder = r"C:\Users\sjwu1\Journal_Data\\Scihub_checked"

total=0
fulllist_s_1940=0
for ind in temp2.index:
    temp3=temp[temp['issue_url']==temp2['issue_url'][ind]]
    downloaded=0
    uploaded = 0
    for ind2 in temp3.index:
        pdf_file_name=temp['stable_url'][ind2].split('/')[-1]+".pdf"
        if (temp2['year'][ind]==1984):
            fulllist_s_1940+=1
            #print(pdf_file_name+" "+str(os.path.isfile(directory+pdf_file_name)))
            upload_indicator=1 #defaults to upload - we can handle duplicates
            try:
                page_token = None
                while True:
                    # Call the Drive v3 API
                    # "mimeType = 'application/vnd.google-apps.folder'" # files that are folders
                    # "name ='354.pdf'" #search by name
                    response = service.files().list(q="name ='"+pdf_file_name+"'",
                        fields="nextPageToken, files(id,name)",
                        pageToken=page_token).execute()
                    items = response.get('files', [])                
                    if (len(items)>0):
                        uploaded+=1
                        #service.files().delete(fileId=items[0]['id']).execute()
                        print(u'already uploaded: {0} ({1})'.format(items[0]['name'], items[0]['id']))
                        upload_indicator=0
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                    print(count)
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f'An error occurred: {error}')
            if(os.path.isfile(directory+"\\"+pdf_file_name)):
                downloaded+=1
                if (upload_indicator==1):
                    try:
                        file_metadata = {'name': pdf_file_name, 'parents': ["1DJ0Ph_-JWSvkzzI70EVCU9JRb1jMp_cO"]}
                        media = MediaFileUpload(directory+"\\"+pdf_file_name, mimetype='application/pdf', resumable=True)
                        file = service.files().create(body=file_metadata,
                                                            media_body=media,
                                                            fields='id').execute()
                        print ('File ID: '+ file.get('id'))
                        uploaded+=1
                    except Exception as e:
                        print(e)
                #source = directory + "\\"+ pdf_file_name
                #destination = dst_folder +"\\"+ pdf_file_name
                #shutil.move(source,destination)
    total=total+downloaded
    print(str(temp2['year'][ind])+" "+str(temp2['no_docs'][ind])+" "+str(temp2['issue_url'][ind])+" "+str(downloaded)+ " "+str(uploaded))

print('total downloaded: ' + str(total))
print('total papers after 1940: '+str(fulllist_s_1940))
