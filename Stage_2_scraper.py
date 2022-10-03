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

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'

def accept_cookies(driver):
    try:
        WebDriverWait(driver, 15).until(
            expected_conditions.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
        )
        driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
    except Exception as e:
        print('no cookies')
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
def recaptcha_check2(driver):
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'viewer-error'))
        )
        style=driver.find_element(By.CLASS_NAME, 'viewer-error').get_attribute('style')
        if style=='display: none;':
            print('no_recaptcha')
        else:
            recaptcha_note()
            print('recaptcha found\nplease pass recaptcha and allow to resolve\nthen press enter to continue')
            driver.refresh()
            input()
            recaptcha_check(driver)
    except Exception as e:
        recaptcha_note()
        print('recaptcha found\nplease pass recaptcha and allow to resolve\nthen press enter to continue')
        driver.refresh()
        input()
        recaptcha_check(driver)  


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
        print("passed")
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


def seek(driver, issue_URL, masterlist, ID):
 #not yet implemented
    return 0

def Run(driver, masterlist, lib_URL, directory, URL_starts,sleep_time):
    throttle=0
    print(lib_URL)
    for ind in URL_starts.index:
        # finding a suitable pivot point to reduce travel
        issue_masters=masterlist[masterlist['issue_url']==URL_starts['issue_url'][ind]]
        downloaded=0
        #building a set of what doesn't exist
        container=[]
        for a in issue_masters.index:
            path = directory / (issue_masters['URL'][a].split("/")[-1]+".pdf")
            ref_filepath = directory / (issue_masters['URL'][a].split("/")[-1]+".json")
            
            if (not os.path.exists(ref_filepath)) or (not os.path.exists(path)):
                # point it at the first URL that hasn't been scraped for references or the pdf
                driver.get(regex.sub(r'http://(.+?)/', r'https://'+lib_URL+'/', issue_masters['URL'][a]))
                print('starting from: '+issue_masters['URL'][a])
                print(str(downloaded) + ' complete references and pdfs downloaded')
                break
            downloaded+=1
        
        time.sleep(5+sleep_time*random.random())
        if (downloaded==issue_masters.shape[0]):
            continue    
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
                #recaptcha_note()
                input()
            
            #recaptcha_check2(driver)

            url=driver.find_element(By.CLASS_NAME, 'stable-url').text
            path = directory/(url.split("/")[-1]+".pdf")
            ref_filepath = directory/(url.split("/")[-1]+".json")
            #check if the record is complete ie: scraped references and pdfs
            if (os.path.exists(ref_filepath)) and (os.path.exists(path)):
                try: 
                    print('execute 2')
                    
                    WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.XPATH, ".//mfe-content-details-pharos-icon[@name='chevron-right']"))
                    ) 
                    I=driver.find_element(By.XPATH,".//mfe-content-details-pharos-icon[@name='chevron-right']")
                    # action object creation to scroll
                    driver.execute_script("arguments[0].scrollIntoView(true);", I)
                    I.click()
                except Exception as a:
                    print(a)
                    print("was not able to go to next item")
                    print("seems to have reached end of issue")
                    x=1
                continue
                    
            #locating references
            ref_raw=''
            ref_struct=''
            foot_struct=''
            metadata_tab=None
            try:
                WebDriverWait(driver,10).until(
                    expected_conditions.element_to_be_clickable((By.NAME, 'book'))
                )
                time.sleep(5)
                
                metadata_tab=driver.find_element(By.NAME, "book")
                metadata_tab.click()
                
                time.sleep(2)
                WebDriverWait(driver,10).until(
                    expected_conditions.presence_of_element_located((By.ID, 'references'))
                )
                
                ref_raw= driver.find_element(By.ID, r"references").get_attribute('innerHTML')
                ref_obj2=driver.find_elements(By.XPATH, r"//div[@id='references']/div/div")
                for element in ref_obj2:
                    if (element.find_element(By.CLASS_NAME, r"reference-block-title").text=='[Footnotes]'):
                        for k in element.find_elements(By.XPATH, r".//ul/li[@class='reference-list__item']"):
                            foot_struct+=k.find_element(By.XPATH, r".//div/div[@class='media-img']/span[@class='right']").text +'__'
                            try:
                            
                                temp=k.find_elements(By.XPATH, ".//div/div/div/ul/li")
                                if len(temp)>0:
                                    for y in temp:
                                        foot_struct+=y.text+'--'
                                        try:
                                            foot_struct+=y.find_element(By.XPATH, ".//content-viewer-pharos-link").get_attribute('href')+'\n'
                                        except:
                                            foot_struct+='no_crossref\n'
                                else:
                                    raise 1
                            except:
                                temp=k.find_element(By.XPATH, ".//div/div[@class='media-body reference-contains']")
                                foot_struct+=temp.text+'--'
                                try:
                                    foot_struct+=temp.find_element(By.XPATH, ".//content-viewer-pharos-link").get_attribute('href')+'\n'
                                except:
                                    foot_struct+='no_crossref\n'
                    else:
                        for k in element.find_elements(By.XPATH, r".//ul/li[@class='reference-list__item']"):
                            ref_struct+=k.text+'--'
                            try:
                                ref_struct+=k.find_element(By.XPATH, ".//content-viewer-pharos-link").get_attribute('href')+'\n'
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
                
            time.sleep(3+random.random())
            if metadata_tab != None:
                try:
                    time.sleep(5)
                    WebDriverWait(driver,10).until(
                        expected_conditions.presence_of_element_located((By.NAME, "info-inverse"))
                    )
                    driver.find_element(By.NAME, "info-inverse").click()
                except Exception as e:
                    print(e)
                    print('could not click')
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
                    print("no t&c")

            #need to allow time for download to complete and return to initial page
            time.sleep(15+sleep_time*random.random())

            #inserting this thing
                       
            ref_filename=directory/(url.split("/")[-1]+".json")
            if os.path.exists(ref_filename)==False:
                temp = {'stable_url': url,'raw':ref_raw,'footnotes':foot_struct,'references':ref_struct}
                with open(ref_filename, "w") as outfile:
                    json.dump(temp, outfile) 
            
            # try move to the next article, if it doesn't work, assume the end of the issue has been reached
            try: 
                print('execute 3')
                WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.XPATH, ".//mfe-content-details-pharos-icon[@name='chevron-right']"))
                    ) 
                I=driver.find_element(By.XPATH,".//mfe-content-details-pharos-icon[@name='chevron-right']")
                # action object creation to scroll
                driver.execute_script("arguments[0].scrollIntoView(true);", I)
                I.click()
                time.sleep(0.4)
            except Exception as a:
                print(a)
                try: 
                    WebDriverWait(driver, 20).until(
                    expected_conditions.element_to_be_clickable((By.XPATH, r".//mfe-content-details-pharos-icon[@name='chevron-left']"))
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
    
    print(URL_starts['URL'])
    
    Chrome_driver=get_driver(directory, 'https://www.jstor.org/')
    issue_data=None
    Run(Chrome_driver[0], masters, Chrome_driver[1], directory, URL_starts, sleep_time)
    
    Chrome_driver.close()
    