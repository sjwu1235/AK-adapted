import json
from pathlib import Path
from re import L
import time
import pandas as pd
import random
import os
import regex
import wget
import shutil
import re

from plyer import notification
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


with open(r'Scihub_inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

directory = Path(input_deets['directory'])  
temp = pd.read_excel(input_deets['master'])
print(temp.columns)
temp2 = temp[['issue_url','year']].drop_duplicates()
temp['year']=temp['year'].astype(int)

processed_list=[]
Syear=2012
Eyear=2012
#issues=temp2[temp2['year']==input_deets['year']]['issue_url']
issues=temp2[(temp2['year']>=Eyear)&(temp2['year']<=Syear)]['issue_url']

print(issues)
for i in issues.index:
    dois=temp[temp['issue_url']==issues[i]]
    x=dois['stable_url']
    for j in x.index:
        print(x[j])
        reference_id=x[j].split('jstor.org/stable/')[-1] #shift to regex answer
        print(reference_id)
        if '/' in reference_id:
            processed_list.append(reference_id)
        else:
            processed_list.append('10.2307/'+ reference_id)
    print(dois['stable_url'].shape)
print('executed')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("prefs", {
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True, #It will not show PDF directly in chrome
    "credentials_enable_service": False, # gets rid of password saver popup
    "profile.password_manager_enabled": False #gets rid of password saver popup
})
driver = webdriver.Chrome(service=Service(ChromeDriverManager(version='104.0.5112.79').install()), options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

time.sleep(5)

mirrors=["//zero.sci-hub.se","//moscow.sci-hub.se","//twin.sci-hub.se"]
def get_file(url, name):
    try:
        wget.download(url, name)
        return 1
    except:
        return 0


for i in processed_list:
    if(os.path.exists(directory / (i[8:]+'.pdf'))):
        continue
    driver.get("https://sci-hub.se/"+i)
    time.sleep(20)
    print(i)
    try:
        #temp=driver.find_element(By.XPATH, r".//div[@id='buttons']//button").get_attribute('onclick')[15:-1]
        temp=driver.find_element(By.XPATH, r".//div[@id='buttons']//button").get_attribute('onclick')[15:-1]
        print(temp)
        """
        if 'moscow' in temp:
            print(temp)
            temp=mirrors[0]+temp[19:]
            print(temp)
        """
        print(directory / (i.split('/')[-1]+'.pdf')) 
        wget.download('https:'+temp, str(directory / (i.split('/')[-1]+'.pdf')))
        time.sleep(15)
        print(i)
    except Exception as e:
        print(e)
        print('not loading, document not likely on SciHub')
        try:
            driver.get("https://sci-hub.se/"+i)
            time.sleep(10)
            print('trying an alternative method...')
            temp=driver.find_element(By.XPATH, r".//div[@id='buttons']//button").get_attribute('onclick')[15:-1]
            driver.find_element(By.XPATH, r".//div[@id='buttons']//button").click()
            time.sleep(15) # give it 60 seconds to download
            print(temp)
            filename = re.search("(.*)/(.*)\?download=true",temp).group(2)
            checkfile=directory / filename
            print(checkfile)
            if(filename in os.listdir(directory)):
                os.rename(checkfile, directory / (i[8:]+'.pdf'))
                print('successfully renamed the file!')
            else:
                print('suspected file named '+str(filename)+' that should be named '+i[8:]+'.pdf')
                print('otherwise, check your internet connection... this file just didn\'t download')
        except Exception as a:
            print(a)
            print("nope they really don't have one.")
            time.sleep(15)
        
driver.close()