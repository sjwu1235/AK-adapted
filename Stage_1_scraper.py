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


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
COLS = ['year','issue_url','Jstor_issue_text','journal']
# cookie acceptor
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

def get_citation(driver, attempt, attempt_limit):
    if attempt<attempt_limit:
        time.sleep(5)    
        driver.find_element(By.XPATH, r'.//*[@id="select_all_citations"]//span').click()
       
        time.sleep(3)
        driver.find_element(By.ID, 'bulk-cite-button').click()
        time.sleep(5)
        try:
            WebDriverWait(driver,20).until(
                expected_conditions.presence_of_element_located((By.XPATH, r".//div//mfe-bulk-cite-pharos-dropdown-menu[@id='bulk-citation-dropdown']//mfe-bulk-cite-pharos-dropdown-menu-item[5]"))
                )
            driver.find_element(By.XPATH, r".//div//mfe-bulk-cite-pharos-dropdown-menu[@id='bulk-citation-dropdown']//mfe-bulk-cite-pharos-dropdown-menu-item[5]").click()
            return 1
        except:
            driver.refresh()
            time.sleep(20)
            recaptcha_check(driver)
            return get_citation(driver, attempt+1, attempt_limit)
    else:
        return 0
        

def process_citation(directory, issue_url):
    file_path= directory / "citations.txt"
    final_name=directory / (issue_url.split('https://www.jstor.org/stable/10.2307/')[-1]+'.txt')
    if os.path.exists(final_name)==True:
        file_path=final_name
    
    #poll directory for file existence
    while os.path.exists(file_path)==False:
        time.sleep(5)

    fl=None
    with open(file_path, 'r', encoding="UTF-8") as input_file:
        fl = input_file.read()
        if regex.search('A problem occurred trying to deliver text citation data', fl) is not None:
            fl=None
        fl=fl.replace('\n','').split('@')

    if fl is not None:
        data={}
        count=0
        for i in fl[2:]:
            tp=i.find('{')
            tp2=i.find(',')
            test=i[tp2+1:].replace('{','').split('}, ')
            python_dict={}
            python_dict['type']=i[:tp]
            python_dict['issue_url']=issue_url
            for j in test:
                if '=' in j:
                    temp=j.replace('{','').replace('}','').split('=')
                    python_dict[temp[0].strip()]=temp[1].strip()
            data[count]=python_dict
            count+=1
        os.rename(file_path, final_name)
        #print(data)
        return pd.DataFrame(data).transpose()  
    else:
        print("Citations did not load correctly. Citation file for "+issue_url+" will be deleted. This will be re-downloaded next session. ")
        if os.path.exists(file_path)==True:
            os.remove(file_path)
        return pd.DataFrame()

def get_driver(directory, URL):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-agent={USER_AGENT}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    #chrome_options.add_extension("./extension_1_38_6_0.crx")
    #chrome_options.add_extension("./extension_busters.crx")
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
    #driver.set_window_position(1024, 1024, windowHandle ='current')
    driver.get(URL)
    try:
        WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "content")))
        print("passed")
    except:
        print("Failed to access journal page")
        driver.refresh()
        time.sleep(30)
        recaptcha_check(driver)

    time.sleep(5)
    accept_cookies(driver)
    return driver

def get_issue_list(driver, Jname):
    
    data=pd.DataFrame(columns=COLS)
    
    #//*[@id="content"]/div[2]/collection-view-pharos-layout/div[1]/div[2]/div/div/details[1]/summary/h2
    click=driver.find_elements(By.CLASS_NAME, 'decade__heading')
    #print(click)
    # expand the drawers one by one, sometimes it doesn't work if you bulk click
    try:
        for element in click:
            time.sleep(10)
            element.click()
    except:
        print('Expansion issue')
        driver.refresh()
        time.sleep(30)

    # let everything settle
    time.sleep(10)
    print('Please ensure that everything is expanded. Then press enter.')
    print('else reload page and expand all years manually and then continue.')
    input()
    decade_List=driver.find_elements(By.XPATH,r".//dd//ul//li")
    for element in decade_List:
        year_list=element.find_elements(By.XPATH, r".//ul//li//collection-view-pharos-link")
        temp=element.get_attribute('data-year')
        if temp==None:
            continue
        print(temp)
        for item in year_list:
            data=pd.concat([data, pd.DataFrame([{'year':int(temp),'issue_url':'https://www.jstor.org'+item.get_attribute('href'), 'Jstor_issue_text':item.text, 'journal':Jname}])], ignore_index=True )
    return data


def Run(driver, directory, data):
    throttle=0
    masterlist=pd.DataFrame()
    
    for ind in data.index:   
        time.sleep(5*random.random())   
        file_path=directory / (data['issue_url'].iloc[ind].split('https://www.jstor.org/stable/10.2307/')[-1]+'.txt')
        print(file_path)
        #poll directory for file existence
        if os.path.exists(file_path)==False:

            driver.get(data['issue_url'].iloc[ind])
            try:
                WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "toc-export-list")))
            except:
                print("Timed out: manually resolve the page to "+ data['issue_url'].iloc[ind])
                print("Press enter to continue after page completely loads")
                input()
                recaptcha_check(driver)
                
            time.sleep(5+throttle)
            accept_cookies(driver)
                        
            indicator=get_citation(driver, 0, 10)
            if indicator == 0: 
                print('Unknown problem')
                print('Please refresh and download citation.txt from '+ data['issue_url'].iloc[ind] + 'and rename to ' + data['issue_url'].iloc[ind].split('/')[-1] +'.txt')
                print('Press Enter to continue')
                input()

        masterlist=pd.concat([masterlist, process_citation(directory, data['issue_url'].iloc[ind])], ignore_index=True)
    return masterlist
        
if __name__ == "__main__":
    # Journal page URL
    with open(r'inputs.json', 'r') as input_file:
        input_deets = json.load(input_file)

    URL = input_deets['journal_URL']
    directory = Path(input_deets['directory'])
    Jname=input_deets['journal_name']
    pivots=Path(input_deets['pivots'])
    masters=Path(input_deets['master'])
    
    Chrome_driver=get_driver(directory, URL)
    issue_data=None

    if input_deets['pivot_scrape_indicator']==1:
        issue_data=get_issue_list(Chrome_driver, Jname)
        issue_data.to_excel(pivots, index=False)
    else:
        issue_data=pd.read_excel(pivots)

    output=Run(Chrome_driver, directory, issue_data)
    
    if len(output['issue_url'].unique())==len(issue_data):
        output.to_excel(masters, index=False)
    else:
        print('Rerun scraper. Masterlist incomplete')
    Chrome_driver.close()