import json
from pathlib import Path
import time
import pandas as pd
import random
import os
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import regex

pd.set_option('display.max_rows', None)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
COLS = ['year','issue_url','Jstor_issue_text','journal']

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
        print('recaptcha found')
        print('please pass recaptcha and allow to resolve')
        print('then press enter to continue')
        input()
        recaptcha_check(driver)
    except Exception as e:
        print('no_recaptcha')
        #print(e)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'px-captcha'))
        )
        print('recaptcha found')
        print('please pass recaptcha and allow to resolve')
        print('then press enter to continue')
        driver.refresh()
    except Exception as e:
        print('no_recaptcha')
        #print(e)

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
            expected_conditions.element_to_be_clickable((By.ID, "searchBox"))
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
    print(lib_URL)
    return [driver, lib_URL]


def seek(driver, issue_URL, masterlist, ID):
 #not yet implemented
    return 0

def Run(driver, masterlist, lib_URL, directory, URL_starts,datadump,sleep_time):
    throttle=0
    print(lib_URL)
    for ind in URL_starts.index:
        # finding a suitable pivot point to reduce travel
        issue_masters=masterlist[masterlist['issue_url']==URL_starts['issue_url'][ind]]
        downloaded=0
        
        for a in issue_masters.index:
            path = directory / (issue_masters['URL'][a].split("/")[-1]+".pdf")
            print(issue_masters['URL'][a].split("/")[-1] not in datadump)
            print(not os.path.isfile(path))
            
            
            if (issue_masters['URL'][a].split("/")[-1] not in datadump) or (not os.path.exists(path)):
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
                print('execute 1')
                WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "metadata-info-tab-contents")))
            except:
                print("Article page not loading")
                print("Please resolve page to" + driver.current_url)
                print("Then enter to continue")
                input()
            
            url=driver.find_element(By.CLASS_NAME, 'stable-url').text
            path = directory/(url.split("/")[-1]+".pdf")
            
            #check if the record is complete ie: scraped references and pdfs
            if (issue_masters['URL'][a].split("/")[-1] in datadump) and (os.path.exists(path)):
                try: 
                    print('execute 2')
                    WebDriverWait(driver, 20).until(
                        expected_conditions.presence_of_element_located((By.ID, 'metadata-info-tab-contents'))
                        ) 
                    time.sleep(10)
                    driver.find_element(By.XPATH,r".//content-viewer-pharos-link[@data-sc='text link:next item']").click()
                except:
                    print("was not able to go to next item")
                    print("seems to have reached end of issue")
                    x=1
                    with open("datadump.json", "w") as outfile:
                        json.dump(datadump, outfile) 
                continue
                    
            #locating references
            ref_raw=''
            ref_struct=''
            foot_struct=''
            try:
                #WebDriverWait(driver,10).until(
                #    expected_conditions.presence_of_element_located((By.CLASS_NAME, 'metadata-info-tab'))
                #)
                time.sleep(5)
                #//*[@id="content-viewer-container"]/div[2]/div[1]/div[2]/button[2]/span
                metadata_tabs=driver.find_elements(By.CLASS_NAME, r"metadata-info-tab-title")
                for elem in metadata_tabs:
                    if elem.text=='References':
                        elem.click()
                
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
            
            driver.find_element(By.CLASS_NAME, r"metadata-info-tab-title").click()

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
            time.sleep(10+sleep_time*random.random())

            #inserting this thing
        
            if (issue_masters['URL'][a].split("/")[-1] not in datadump)&(os.path.exists(path)):
                datadump[issue_masters['URL'][a].split("/")[-1]] = {'stable_url': url,'raw':ref_raw,'footnotes':foot_struct,'references':ref_struct}
                with open("datadump.json", "w") as outfile:
                    json.dump(datadump, outfile) 
            
            # try move to the next article, if it doesn't work, it dumps the data assuming the end of the issue has been reached
            try: 
                WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.XPATH, ".//mfe-content-details-pharos-link[@data-sc='text link:next item']"))
                    ) 
                driver.find_element(By.XPATH, r".//mfe-content-details-pharos-link[@data-sc='text link:next item']").click()
                #print('execute 3')
            except:
                try: 
                    WebDriverWait(driver, 20).until(
                    expected_conditions.presence_of_element_located((By.XPATH, r".//mfe-content-details-pharos-link[@data-sc='text link:previous item']"))
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

    directory = Path(input_deets['directory'])
    Jname=input_deets['journal_name']
    pivots=pd.read_excel(Path(input_deets['pivots']))
    masters=pd.read_excel(Path(input_deets['master']))
    directory = Path(input_deets['directory'])

    start_year=input_deets['start_year']
    end_year=input_deets['end_year']
    sleep_time=input_deets['sleep_time']
    URL_starts = masters[(masters['year']>=start_year)&(masters['year']<=end_year)].sort_values(['issue_url','URL'], axis=0).groupby('issue_url').head(1)

    datadump={}
    if (os.path.isfile('datadump.json')):
        with open(r'datadump.json', 'r') as input_file:
            datadump = json.load(input_file)
    
    print(URL_starts['URL'])
    
    Chrome_driver=get_driver(directory, 'https://www.jstor.org/')
    issue_data=None
    Run(Chrome_driver[0], masters, Chrome_driver[1], directory, URL_starts, datadump, sleep_time)
    
    Chrome_driver.close()
    