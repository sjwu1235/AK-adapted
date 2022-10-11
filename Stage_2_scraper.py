import json
from pathlib import Path
import time
import pandas as pd
import random
import os

#from plyer import notification
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import regex

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.61 Safari/537.36'

def accept_cookies(driver):
    try:
        WebDriverWait(driver, 15).until(
            expected_conditions.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
        )
        driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    except Exception as e:
        print(r'no cookies')
        #print(e)
        
def recaptcha_check(driver):
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'px-captcha'))
        )
        #recaptcha_note()
        print('recaptcha found\nplease pass recaptcha and allow to resolve\nthen press enter to continue')
        input()
        recaptcha_check(driver)
    except Exception as e:
        print('no_recaptcha')
        #print(e)
'''
def recaptcha_note():
    notification.notify(
        app_name='Stage_2_scraper.py',
        title = "Scraper Stall",
        message="Recaptcha detected, please resolve then enter on command line to continue" ,
        ticker='Help!',
        timeout=30)
'''

def get_driver(directory, URL):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": str(directory), #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True, #It will not show PDF directly in chrome
        "credentials_enable_service": False, # gets rid of password saver popup
        "profile.password_manager_enabled": False #gets rid of password saver popup
    })
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print('Attempting to connect to JSTOR', end = '\r')
    print('\n\nInstructions\n\n')
    print('1. Login to institution')
    print('2. Navigate to home page of jstor')
    print('3. Please accept cookies.')
    print('\n... press Enter once complete to continue\n\n')
    driver.get(URL)
    input()

    print('\nChecking for successful logon')
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, "Query"))
        )
        print(r"passed")
        time.sleep(5)
    except Exception as e:
        print(e)
        print("Unable to load search page")
        driver.refresh()
        time.sleep(30)
        recaptcha_check(driver)
        accept_cookies(driver)
    time.sleep(5)
    lib_URL=regex.search('https://(.+?)/', driver.current_url).group(1)
    return [driver, lib_URL]


def Run(driver, masterlist, lib_URL, directory, URL_starts,sleep_time):
    print(lib_URL)
    throttle=0
    for ind in URL_starts.index:
        # finding a suitable pivot point to reduce travel
        issue_masters=masterlist[masterlist['issue_url']==URL_starts['issue_url'][ind]]
        downloaded=0
        #building a set of what doesn't exist
        container=[]
        for a in issue_masters.index:
            path = directory / (issue_masters['URL'][a].split("/")[-1]+".pdf")
            if (not os.path.exists(path)):
                # point it at the first URL that hasn't been scraped for references or the pdf
                container.append(issue_masters['URL'][a])
            else:
                downloaded+=1
        if (downloaded==issue_masters.shape[0]):
            continue 
        driver.get(regex.sub(r'htt(p|ps)://(.+?)/', r'https://'+lib_URL+'/', container[0]))
        print('starting from: '+container[0])
        container.pop(0)
        print(str(downloaded) + ' of '+str(issue_masters.shape[0])+' complete references and pdfs downloaded')
        time.sleep(5+sleep_time*random.random())
        x=0
        while x==0:
            accept_cookies(driver)
            try:
                WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "metadata-info-tab-contents")))
            except Exception as a:
                print(a)
                print("Article page not loading")
                print("Please resolve page to" + driver.current_url)
                print("Then enter to continue")
                input()

            url=driver.find_element(By.CLASS_NAME, 'stable-url').text
            path = directory/(url.split("/")[-1]+".pdf")
            time.sleep(3+random.random())
            
            #click download but only if not there already
            if not os.path.isfile(path):
                driver.find_element(By.XPATH, r".//mfe-download-pharos-button[@data-sc='but click:pdf download']").click()
                # bypass t&c
                try:
                    WebDriverWait(driver, 10).until(
                        expected_conditions.presence_of_element_located((By.ID, 'content-viewer-container'))
                        ) 
                    driver.find_element(By.XPATH, r".//mfe-download-pharos-button[@data-qa='accept-terms-and-conditions-button']").click()
                except:
                    print(r"no t&c")

            #need to allow time for download to complete and return to initial page
            time.sleep(15+sleep_time*random.random())
            
            # try move to the next article, if it doesn't work, assume the end of the issue has been reached
            try: 
                WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.XPATH, ".//mfe-content-details-pharos-icon[@name='chevron-right']"))
                    ) 
                I=driver.find_element(By.XPATH,".//mfe-content-details-pharos-icon[@name='chevron-right']")
                link=driver.find_elements(By.XPATH,".//*[@id='issue-pager']//mfe-content-details-pharos-link")[-1].get_attribute('href')

                if len(container)==0:
                    x=1
                elif link.split('/')[-1]!=container[0]:
                    driver.get(regex.sub(r'htt(p|ps)://(.+?)/', r'https://'+lib_URL+'/', container[0]))
                    container.pop(0)
                else:
                    # action object creation to scroll
                    driver.execute_script("arguments[0].scrollIntoView(true);", I)
                    I.click()
                    time.sleep(0.4*sleep_time)
            except Exception as a:
                try: 
                    WebDriverWait(driver, 20).until(
                    expected_conditions.element_to_be_clickable((By.XPATH, r".//mfe-content-details-pharos-icon[@name='chevron-left']"))
                    ) 
                    x=1
                except:
                    print("Stall, possible recaptcha, please resolve stall to "+url)
                    print("Enter to continue once page is resolved")
                    input()

if __name__ == "__main__":
    # Journal page URL
    with open(r'inputs.json', 'r') as input_file:
        input_deets = json.load(input_file)

    Jname=input_deets['journal_name']
    pivots=pd.read_excel(Path(input_deets['pivots']))
    masters=pd.read_excel(Path(input_deets['master']))
    directory = Path(input_deets['directory'])

    start_year=input_deets['start_year']
    end_year=input_deets['end_year']
    sleep_time=input_deets['sleep_time']
    URL_starts = masters[(masters['year']>=start_year)&(masters['year']<=end_year)].sort_values(['issue_url','URL'], axis=0).groupby('issue_url').head(1)
    Chrome_driver=get_driver(directory, 'https://www.jstor.org/')
    issue_data=None
    Run(Chrome_driver[0], masters, Chrome_driver[1], directory, URL_starts, sleep_time)
    
    Chrome_driver[0].close()
    