from __future__ import print_function
from ast import Not
import json
from pathlib import Path
import time
import pandas as pd
import os.path
import random
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly','https://www.googleapis.com/auth/drive.file']
KEY_FILE_LOCATION = 'credentials.json'

# this is the folder id for the destination folder on google drive
# # it is set manually to a folder called Crowd Sourcing
               
               
folder_id = "1DJ0Ph_-JWSvkzzI70EVCU9JRb1jMp_cO"
creds = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)
service = build('drive', 'v3', credentials=creds)
count=0

from connection_controllers.gen_connection_controller import GenConnectionController

with open(r'inputs.json', 'r') as input_file:

    input_deets = json.load(input_file)

directory = input_deets['directory']
masterlist = pd.read_excel(input_deets['master'])
start_loc = input_deets['pivots']
start_year=input_deets['start_year']
end_year=input_deets['end_year']
sleep_time=input_deets['sleep_time']
starts = pd.read_excel(start_loc)
URL_starts = starts[(starts['year']>=start_year)&(starts['year']<=end_year)]


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
chrome_options = webdriver.ChromeOptions()

# don't recommend this because this scraper may require some human intervention if it crashes but...
# uncomment below if you dont want the google chrome browser UI to show up.
# chrome_options.add_argument('--headless')

curdir = Path.cwd().joinpath("BrowserProfile")
#chrome_options.add_argument("user-data-dir=selenium") #this is supposed to automatically manage cookies but it's not working
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_extension("./extension_1_38_6_0.crx")
chrome_options.add_extension("./extension_busters.crx")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": directory, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True, #It will not show PDF directly in chrome
    "credentials_enable_service": False, # gets rid of password saver popup
    "profile.password_manager_enabled": False #gets rid of password saver popup
})

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

web_session = GenConnectionController(driver, "https://www.jstor.org")
lib_URL=re.search('https://(.+?)/', driver.current_url).group(1)

def isUpload(file_name):
    try:
        upload_indicator=True #false for in drive so don't upload and true not in drive so upload required
        page_token = None
        while True:
            # Call the Drive v3 API
            # "mimeType = 'application/vnd.google-apps.folder'" # files that are folders
            # "name ='354.pdf'" #search by name
            response = service.files().list(q="name ='"+file_name+"'",
                fields="nextPageToken, files(id)",
                pageToken=page_token).execute()
            items = response.get('files', [])                
            if (len(items)>0):
                print(u'{0}'.format(items[0]['id']))
                upload_indicator=False
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
            print(count)
        return upload_indicator
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None

throttle=0
random.seed(time.time())
for ind in URL_starts.index:
    print("New Issue "+ URL_starts['Jstor_issue_text'][ind])

    # finding a suitable pivot point to reduce travel
    issue_masters=masterlist[masterlist['issue_url']==URL_starts['issue_url'][ind]]
    downloaded=0
    
    for a in issue_masters.index:
        path = directory+"\\"+issue_masters['stable_url'][a].split("/")[-1]+".pdf"
        print(not os.path.isfile(path))
        print(issue_masters['stable_url'][a])
        check=isUpload(issue_masters['stable_url'][a].split("/")[-1]+".pdf")
        dataCheck=isUpload(issue_masters['stable_url'][a].split("/")[-1]+".json")
        print(check)
        print(dataCheck)
        if (dataCheck or check):
            # point it at the first URL that hasn't been scraped for references or the pdf
            driver.get(re.sub('https://(.+?)/', 'https://'+lib_URL+'/', issue_masters['stable_url'][a]))
            print('starting from: '+issue_masters['stable_url'][a])
            print(str(downloaded) + ' complete references and pdfs downloaded')
            break
        downloaded+=1
    
    time.sleep(5+sleep_time*random.random())
    if (downloaded==URL_starts['no_docs'][ind]):
        continue    
    x=0
    while x==0:
        
        # code for accepting cookies
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.element_to_be_clickable((By.XPATH, r"//button[@id='onetrust-accept-btn-handler']"))
            )
            driver.find_element_by_xpath(r".//button[@id='onetrust-accept-btn-handler']").click()
            print('cookies accepted')
        except:
            print("Please accept cookies else continue if there aren't any")
        
        try:
            print('execute 1')
            WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "metadata-info-tab")))
        except:
            print("Article page not loading")
            print("Please resolve page to" + driver.current_url)
            print("Then enter to continue")
            input()
        
        url=driver.find_element_by_xpath(r".//div[@class='stable-url']").text
        path = directory+"\\"+url.split("/")[-1]+".pdf"
        
        #check if the record is complete ie: scraped references and pdfs
        check=isUpload(url.split("/")[-1]+".pdf")
        dataCheck=isUpload(url.split("/")[-1]+".json")
        print(check)
        print(dataCheck)
        #check and datacheck evaluate to true if ether the pdf or metadata require uploading
        #hence pdf and json must evaluate to false to result in a skip
        if ((not dataCheck) and (not check)):
            try: 
                print('execute 2')
                WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.ID, 'metadata-info-tab'))
                    ) 
                time.sleep(10)
                driver.find_element_by_xpath(r".//content-viewer-pharos-link[@data-sc='text link:next item']").click()
            except:
                print("was not able to go to next item")
                print("seems to have reached end of issue")
                x=1
            continue
        # edge case: some do have author affiliation and some do not
        affiliations=""
        if (input_deets['affiliations']==1):
            try:
                WebDriverWait(driver, 10).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'contrib-group'))
                        ) 
                author_info=driver.find_elements_by_xpath(r".//div[@class='contrib-group']//div//span")
                count=0
                for item in author_info:
                    if (count%2) == 0:
                        affiliations=affiliations+item.text+' - '
                    else:
                        affiliations=affiliations+item.text+'. '
                    count+=1
                print(affiliations)
            except:
                print('no author affiliation') 
                

        # some articles are rather reviews or comments or replies and will not have abstracts
        abstract=""
        try:
            abstract=driver.find_element_by_xpath(r".//div[@class='abstract']").text
        except:
            abstract=None
        #locating references
        ref_raw=''
        ref_struct=''
        foot_struct=''
        try:
            #WebDriverWait(driver,10).until(
            #    expected_conditions.presence_of_element_located((By.ID, 'metadata-info-tab'))
            #)
            time.sleep(5)
            driver.find_element_by_id(r"reference-tab").click()
            time.sleep(2)
            WebDriverWait(driver,10).until(
                expected_conditions.presence_of_element_located((By.ID, 'reference-tab-contents'))
            )
            ref_obj=driver.find_elements_by_xpath(r"//div[@id='references']/div/div/ul/li")
            ref_raw= driver.find_element_by_xpath(r"//div[@id='references']/div").text
            ref_obj2=driver.find_elements_by_xpath(r"//div[@id='references']/div/div")
            for element in ref_obj2:
                if (element.find_element_by_class_name(r"reference-block-title").text=='[Footnotes]'):
                    for k in element.find_elements_by_xpath(r".//ul/li[@class='reference-list__item']"):
                        foot_struct+=k.find_element_by_xpath(r".//div/div[@class='media-img']/span[@class='right']").text +'__'
                        try:
                           
                            temp=k.find_elements_by_xpath(".//div/div/div/ul/li")
                            if len(temp)>0:
                                for y in temp:
                                    foot_struct+=y.text+'--'
                                    try:
                                        foot_struct+=y.find_element_by_xpath(".//content-viewer-pharos-link").get_attribute('href')+'\n'
                                    except:
                                        foot_struct+='no_crossref\n'
                            else:
                                raise 1
                        except:
                            temp=k.find_element_by_xpath(".//div/div[@class='media-body reference-contains']")
                            foot_struct+=temp.text+'--'
                            try:
                                foot_struct+=temp.find_element_by_xpath(".//content-viewer-pharos-link").get_attribute('href')+'\n'
                            except:
                                foot_struct+='no_crossref\n'
                else:
                    for k in element.find_elements_by_xpath(r".//ul/li[@class='reference-list__item']"):
                        ref_struct+=k.text+'--'
                        try:
                            ref_struct+=k.find_element_by_xpath(".//content-viewer-pharos-link").get_attribute('href')+'\n'
                        except:
                            ref_struct+='no_crossref\n'   
            #print('########### starting ##############')
            #print(foot_struct)
            #print('########### mid ################')
            #print(ref_struct)
            #print("########### fin ################")
            print('references scraped')
        except Exception as e: 
            print(e)
            print('no references in contents')
            
        # text processing for number of pages
        time.sleep(3+random.random())
        
        driver.find_element_by_id(r"metadata-info-tab").click()

        time.sleep(3+random.random())
        
        #click download but only if not there already
        if (check):
            if (not os.path.isfile(path)):
                driver.find_element_by_xpath(r".//mfe-download-pharos-button[@data-sc='but click:pdf download']").click()
            
                # bypass t&c
                try:
                    WebDriverWait(driver, 10).until(
                        expected_conditions.presence_of_element_located((By.ID, 'content-viewer-container'))
                        ) 
                    driver.find_element_by_xpath(r".//mfe-download-pharos-button[@data-qa='accept-terms-and-conditions-button']").click()
                except:
                    print("no t&c")

        #need to allow time for download to complete and return to initial page
        time.sleep(10+sleep_time*random.random())
        if (check):
            if (os.path.isfile(path)):
                try:
                    # Uploading a file
                    file_metadata = {
                        "name": url.split("/")[-1]+".pdf",
                        "parents": [folder_id]
                        }
                    # first argument is path to pdf on local
                    media = MediaFileUpload(path, mimetype="application/pdf")
                    file = service.files().create(body=file_metadata,
                                                        media_body=media,
                                                        fields="id").execute()
                    print("File ID: "+ file.get("id")) 
                except HttpError as error:
                    # TODO(developer) - Handle errors from drive API.
                    print(f'An error occurred: {error}')

        #inserting this thing
        #if json not online and file has been downloaded
        if (dataCheck):
            dict = {'stable_url': url, 'abstract': abstract, 'affiliations':affiliations,'raw':ref_raw,'footnotes':foot_struct,'references':ref_struct}
            with open(directory+"\\"+url.split("/")[-1]+".json", "w") as outfile:
                json.dump(dict, outfile)  
            try:
                # Uploading a file
                file_metadata = {
                    "name": url.split("/")[-1]+".json",
                    "parents": [folder_id]
                    }
                # first argument is path to pdf on local
                media = MediaFileUpload(directory+"\\"+url.split("/")[-1]+".json", mimetype="application/json")
                file = service.files().create(body=file_metadata,
                                                    media_body=media,
                                                    fields="id").execute()
                print("File ID: "+ file.get("id")) 
            except HttpError as error:
                # TODO(developer) - Handle errors from drive API.
                print(f'An error occurred: {error}')

        
        # try move to the next article, if it doesn't work, it dumps the data assuming the end of the issue has been reached
        try: 
            WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.XPATH, ".//content-viewer-pharos-link[@data-sc='text link:next item']"))
                ) 
            driver.find_element_by_xpath(r".//content-viewer-pharos-link[@data-sc='text link:next item']").click()
            #print('execute 3')
        except:
            try: 
                WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.XPATH, r".//content-viewer-pharos-link[@data-sc='text link:previous item']"))
                ) 
                print("Was not able to go to next item. Seems to have reached end of issue")    
                x=1
                #print('execute 4')
            except:
                print("Stall, possible recaptcha, please resolve stall to "+url)
                print("Enter to continue once page is resolved")
                input()
                        
        print(driver.current_url)
        #print('execute 5')
        #print(x)
