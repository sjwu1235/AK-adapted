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

from connection_controllers.gen_connection_controller import GenConnectionController

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
#chrome_options.add_extension("./extension_1_38_6_0.crx")
#chrome_options.add_extension("./extension_busters.crx")
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
starts = pd.read_excel(start_loc)
URL_starts = starts[(starts['year']>=start_year)&(starts['year']<=end_year)]
throttle=0
random.seed(time.time())
for ind in URL_starts.index:
    print("New Issue "+ URL_starts['Jstor_issue_text'][ind])
    # point it at some Jstor start page
    driver.get(re.sub('https://(.+?)/', 'https://'+lib_URL+'/', URL_starts['pivot_url'][ind]))
    time.sleep(5+sleep_time*random.random())    
    x=0
    while x==0:
        try:
            WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "metadata-info-tab")))
            WebDriverWait(driver,10).until(expected_conditions.presence_of_element_located((By.ID, "issue-pager")))
        except:
            print("Article page not loading")
            print("Please resolve page to" + driver.current_url)
            print("Then enter to continue")
            input()
        
        url=driver.find_element_by_xpath(r".//div[@class='stable-url']").text
        path = directory+"\\"+url.split("/")[-1]+".pdf"
        
        #check if it's been downloaded already
        if (datadump[['stable_url']].isin({'stable_url': [url]}).all(1).any())&(os.path.isfile(path)):
            try: 
                WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.ID, 'metadata-info-tab'))
                    ) 
                time.sleep(3)
                driver.find_element_by_xpath(r".//content-viewer-pharos-link[@data-sc='text link:next item']").click()
            except:
                print("was not able to go to next item")
                print("seems to have reached end of issue")
                x=1
                datadump.to_excel(datadump_loc,index=False)  
            continue
        
        #scrape rest of metadata on panel
        content_type=""
        title=""
        author=""
        reviewed_work=""
        '''
        try:
            title=driver.find_element_by_xpath(r".//content-viewer-pharos-heading[@data-qa='item-title']").text
            author=driver.find_element_by_xpath(r".//div[@class='contrib']").text
        except:
            try:
                title=driver.find_element_by_xpath(r".//pharos-heading[@data-qa='item-title']").text
                author=driver.find_element_by_xpath(r".//div[@class='contrib review-text']").text
                reviewed_work=driver.find_element_by_xpath(r".//div[@class='rw reviewed-work__container']").text
            except:
                print("review type")
        '''
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

        
        # text processing for number of pages
        src_info=driver.find_element_by_xpath(r".//div[@data-qa='item-src-info']").text
        
        temp2=src_info.split()
        no_pages=temp2[-2][1:]
        #pages=temp2[-3]
     
        
        pages=""
        #no_pages=""
        #src_info=""
        # some articles are rather reviews or comments or replies and will not have abstracts
        abstract=""
        try:
            abstract=driver.find_element_by_xpath(r".//div[@class='abstract']").text
        except:
            abstract=None

        #click download
        if not os.path.isfile(path):
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
        time.sleep(5+sleep_time*random.random())

        #inserting this thing
    
        if (not datadump[['stable_url']].isin({'stable_url': [url]}).all(1).any())&(os.path.isfile(path)):
            dict = {'stable_url': url, 'authors': author, 'content_type': content_type, 'reviewed_work': reviewed_work, 'title': title, 'abstract': abstract, 'src_info':src_info, 'affiliations':affiliations, 'issue_url':URL_starts['pivot_url'][ind], 'pages': pages,"no_pages": no_pages}
            datadump=datadump.append(dict, ignore_index=True)
        
        # try move to the next article, if it doesn't work, it dumps the data assuming the end of the issue has been reached
        try: 
            WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.ID, 'metadata-info-tab'))
                ) 
            driver.find_element_by_xpath(r".//content-viewer-pharos-link[@data-sc='text link:next item']").click()
        except:
            try: 
                WebDriverWait(driver, 20).until(
                expected_conditions.presence_of_element_located((By.XPATH, r".//content-viewer-pharos-link[@data-sc='text link:previous item']"))
                ) 
                print("Has previous. No next. Seems to have reached end of issue")
                datadump.to_excel(datadump_loc,index=False)     
                x=1
            except:
                print("Stall, possible recaptcha, please resolve stall to "+url)
                print("Enter to continue once page is resolved")
                input()
        
        print(driver.current_url)
