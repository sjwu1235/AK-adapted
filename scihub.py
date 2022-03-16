import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import os
import wget
import shutil


with open(r'Scihub_inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

directory = input_deets['directory']    
temp = pd.read_excel(input_deets['master'])
temp2 = pd.read_excel(input_deets['pivots'])

#temp1 = pd.read_excel(input_deets['scopus'])

processed_list=[]
issues=temp2[temp2['year']==input_deets['year']]['issue_url']
for i in issues.index:
    dois=temp[temp['issue_url']==issues[i]]
    x=dois['stable_url']
    for j in x.index:
        processed_list.append('10.2307'+x[j][x[j].rfind('/'):])
    print(dois['stable_url'].shape)


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.
# not reccommended
#chrome_options.add_argument('--headless')

chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")


chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "C:\\Users\\sjwu1\\Journal_Data\\Scihub", #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True, #It will not show PDF directly in chrome
    "credentials_enable_service": False, # gets rid of password saver popup
    "profile.password_manager_enabled": False #gets rid of password saver popup
})
throttle=0

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
time.sleep(5)
'''
# This section uses scopus DOIs which may be necessary for newer issues
temp3=temp1[temp1['year']==input_deets['year']]
print(temp3)
for i in temp3.index:
    if '10.2307'in temp3['DOI'][i]:
        DOI=temp3['DOI'][i][8:]
        driver.get("https://sci-hub.se/"+temp3['DOI'][i])
        if(DOI+'.pdf' in os.listdir("C:\\Users\\sjwu1\\Journal_Data\\Scihub")):
            continue
        time.sleep(5)
        try:
            wget.download(driver.find_element_by_xpath(r".//div[@id='buttons']//button").get_attribute('onclick')[15:-1],"C:\\Users\\sjwu1\\Journal_Data\\Scihub\\"+DOI+'.pdf')
            time.sleep(10)
            print(DOI)
        except:
            print('not loading, document not likely on SciHub')
            time.sleep(10)
    else:
        print("DOI not in sync with JSTOR: "+temp3['DOI'][i])
'''

mirrors=["//zero.sci-hub.se","//moscow.sci-hub.se","//twin.sci-hub.se"]
def get_file(url, name):
    try:
        wget.download(url, name)
        return 1
    except:
        return 0

def download_wait(path_to_downloads):
    waits = 0
    dl_wait = True
    while dl_wait and waits < 3:
        time.sleep(20)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload') or fname.endswith('.tmp'):
                print(fname)
                dl_wait = True
        waits += 1
    return waits

for i in processed_list:
    if(i[8:]+'.pdf' in os.listdir(directory)):
        continue
    driver.get("https://sci-hub.se/"+i)
    time.sleep(20)
    try:
        temp=driver.find_element_by_xpath(r".//div[@id='buttons']//button").get_attribute('onclick')[15:-1]
        print(temp)
        '''
        if 'moscow' in temp:
            print(temp)
            temp=mirrors[0]+temp[19:]
            print(temp)
        '''
        wget.download('https:'+temp, directory+'\\'+i[8:]+'.pdf')
        time.sleep(15)
        print(i)
    except Exception as e:
        print(e)
        print('not loading, document not likely on SciHub')
        before=len(os.listdir(directory))
        try:
            driver.find_element_by_xpath(r".//div[@id='buttons']//button").click()
            time.sleep(60) # give it 60 seconds to download
            after=len(os.listdir(directory))
            if(after-before!=1):
                raise 'no no no nothing'
            print(os.path.join(directory+'\\',filename))
            filename = max([f for f in os.listdir(directory)], key=os.path.getctime)
            shutil.move(os.path.join(directory+'\\',filename), directory+'\\'+i[8:]+'.pdf')
        except Exception as a:
            print(a)
            print("nope they really don't have one.")
            time.sleep(15)
        
