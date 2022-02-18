# todo
'''
import json
from pathlib import Path
import pathlib
import time
import pandas as pd
import os.path
import selenium 
import re
import abc
import random
import math
import openpyxl

import webdriver_manager

print(selenium.__version__)
print(json.__version__)
print(pd.__version__)
print(re.__version__)
print(openpyxl.__version__)
print(webdriver_manager.__version__)
'''

import json
from pathlib import Path
import time
import pandas as pd
import os.path

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

with open(r'inputs.json', 'r') as input_file:

    input_deets = json.load(input_file)

directory = input_deets['directory']
datadump_loc = input_deets['datadump']
datadump=pd.read_excel(datadump_loc)
start_loc = input_deets['pivots']
start_year=input_deets['start_year']
end_year=input_deets['end_year']
sleep_time=input_deets['sleep_time']

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
chrome_options = webdriver.ChromeOptions()

# don't recommend this because this scraper may require some human intervention if it crashes but...
# uncomment below if you dont want the google chrome browser UI to show up.
#chrome_options.add_argument('--headless')

curdir = Path.cwd().joinpath("BrowserProfile")

chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_extension("./extension_1_38_6_0.crx")
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

dict = {'stable_url': None, 'authors': None, 'content_type': None, 'reviewed_work': None, 'title': None, 'abstract': None, 'src_info': None, 'affiliations':None, 'issue_url':None, 'pages': None,"no_pages": None}

cols=['stable_url', 'authors', 'title','abstract','content_type','issue_url', 'pages']
masterlist=pd.DataFrame(columns=cols)
temp={'stable_url' : None, 'authors' : None, 'title' : None,'abstract' : None,'content_type' : None,'issue_url' : None, 'pages' : None}

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

driver.get('https://www.jstor.org/stable/i331413')
time.sleep(10)
try:
    WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "bulk_citation_export_form")))
except:
    #print("Timed out: manually resolve the page to https://www.jstor.org/"+data['issue_url'][ind][40:])
    print("Press enter to continue after page completely loads")
    input()

all_docs=driver.find_elements_by_xpath(r".//div[@class='media-body media-object-section main-section']")
for item in all_docs:
    temp['stable_url'] = item.find_element_by_xpath(r".//div[@class='stable']").text
    temp['title'] = item.find_element_by_xpath(r".//a[@data-qa='content title']").text
    #temp['issue_url']
    temp2=item.text.split('\n')[0].split('p.')
    if len(temp2)>1:
        temp['pages']=temp2[-1][:-1]
    print(temp2)
    try:
        temp['authors']= item.find_element_by_xpath(r".//div[@class='contrib']").text
    except:
        temp['authors']=None
        print('no authors')
    masterlist=masterlist.append(temp, ignore_index=True)
    
#data['no_docs'][ind]=len(all_urls)
issue_data=driver.find_element_by_xpath(r".//h1//div[@class='issue']").text.split(',')
print(issue_data)
print(len(all_docs))
masterlist.to_excel("out_test.xlsx")
'''
data['volume'][ind]=int(issue_data[0].split()[1])
try:
    data['issue'][ind]=issue_data[1].split()[1].replace('/','-')
    data['month'][ind]=issue_data[2].split()[0]
except:
    print('No issue or month metadata. Possibly is supplement, index or special issue')

'''


