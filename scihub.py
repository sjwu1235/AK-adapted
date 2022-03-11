import json
from pathlib import Path
import time
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import os
import shutil
import urllib
import wget



with open(r'inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

directory = input_deets['directory']    
temp = pd.read_excel(directory+"\\Master lists\\QJE_master.xlsx")
temp2 = pd.read_excel(directory+"\\pivots\\QJE_pivots.xlsx")
temp1 = pd.read_excel(directory+"\\Scopus\\QJE_SCOPUS.xlsx")
# Journal page URL
URL = 'https://sci-hub.se/10.2307/1828153'
directory = input_deets['directory']

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.
# not reccommended
#chrome_options.add_argument('--headless')

chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_extension("./extension_1_38_6_0.crx")
chrome_options.add_extension("./extension_busters.crx")
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

temp3=temp1[temp1['year']==1941]
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
            time.sleep(5)
    else:
        print("DOI not in sync with JSTOR: "+temp3['DOI'][i])

