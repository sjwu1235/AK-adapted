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


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
COLS = ['year', 'month', 'volume', 'issue','issue_url','Jstor_issue_text','journal', 'pivot_url', 'no_docs']
# cookie acceptor
def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, r"//button[@id='onetrust-accept-btn-handler']"))
        )
        driver.find_element(By.XPATH, r".//button[@id='onetrust-accept-btn-handler']").click()
    except:
        print('no cookies')

def get_citation(driver, attempt, attempt_limit):
    if attempt<attempt_limit:
        time.sleep(5)    
        driver.find_element(By.XPATH, r".//toc-view-pharos-checkbox[@id='select_all_citations']//span").click()
        time.sleep(2)
        driver.find_element(By.XPATH, r".//div[@id='export-bulk-drop']//toc-view-pharos-button").click()
        time.sleep(5)
        try:
            #/html/body/main/div[2]/toc-view-pharos-layout/div[1]/div[3]/div/div/toc-view-pharos-dropdown-menu/toc-view-pharos-dropdown-menu-item[5]
            WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.XPATH, r".//div//toc-view-pharos-dropdown-menu[@id='bulk-citation-dropdown']//toc-view-pharos-dropdown-menu-item[5]")))
            driver.find_element(By.XPATH, r".//div//toc-view-pharos-dropdown-menu[@id='bulk-citation-dropdown']//toc-view-pharos-dropdown-menu-item[5]").click()
            return 1
        except:
            driver.refresh()
            time.sleep(8)
            return get_citation(driver, attempt+1, attempt_limit)
    else:
        return 0
        

def process_citation(directory, issue_url):
    file_path=directory+'\\'+"citations.txt"

    #poll directory for file existence
    while os.path.exists(file_path)==False:
        time.sleep(5)
    fl=None
    with open(file_path, 'r', encoding="UTF-8") as input_file:
        fl = input_file.read().replace('\n','').split('@')

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
    os.rename(file_path,directory + '\\'+issue_url.split('https://www.jstor.org/stable/10.2307/')[-1]+'.txt')
    #print(data)
    return pd.DataFrame(data).transpose()  

def get_driver(directory, URL):
    chrome_options = webdriver.ChromeOptions()
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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get(URL)
    try:
        WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "facets-container")))
        print("passed")
    except:
        print("Failed to access journal page")
        raise
    accept_cookies(driver)
    return driver

def Run(driver, Jname, directory):
    throttle=0
    data=pd.DataFrame(columns=COLS)
    masterlist=pd.DataFrame()
    click=driver.find_elements(By.XPATH, r".//dl[@class='facet accordion']//dl//dt//a")
    # expand the drawers one by one, sometimes it doesn't work if you bulk click
    for element in click:
        time.sleep(5)
        element.click()
    # let everything settle
    time.sleep(10)

    decade_List=driver.find_elements(By.XPATH,r".//dd//ul//li")
    for element in decade_List:
        year_list=element.find_elements(By.XPATH, r".//ul//li//a")
        temp=element.get_attribute('data-year')
        if temp==None:
            continue
        print(temp)
        for item in year_list:
            data=pd.concat([data, pd.DataFrame([{'year':int(temp), 'month':None, 'volume':None, 'issue':None, 'issue_url':item.get_attribute('href'), 'Jstor_issue_text':item.text, 'journal':Jname, 'pivot_url':None, 'no_docs':None}])], ignore_index=True )
    print(data)
    for ind in data.index:   
        time.sleep(5*random.random())     
        driver.get(data['issue_url'][ind])
        try:
            WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "bulk_citation_export_form")))
        except:
            print("Timed out: manually resolve the page to"+ data['issue_url'])
            print("Press enter to continue after page completely loads")
            input()
            
        time.sleep(5+throttle)
        accept_cookies(driver)
        all_docs=driver.find_elements(By.XPATH, r".//div[@class='toc-item']")
        data['no_docs'][ind]=len(all_docs)
        issue_data=driver.find_element(By.XPATH, r".//div[@class='issue']").text.split(',')
        data['volume'][ind]=int(issue_data[0].split()[1])
        try:
            data['issue'][ind]=issue_data[1].split()[1].replace('/','-')
            data['month'][ind]=issue_data[2].split()[0]
        except:
            print('No issue or month metadata. Possibly is supplement, index or special issue')
        
        indicator=get_citation(driver, 0, 10)
        if indicator == 0: 
            print('Problem')
            print('Please refresh and download citation.txt from '+ data['issue_url'][ind] + 'and rename to ' + data['issue_url'][ind].split('/')[-1] +'.txt')
            print('Press Enter to continue')
            input()

        masterlist=pd.concat([masterlist, process_citation(directory, data['issue_url'][ind])], ignore_index=True)
        
    return ([data, masterlist])

if __name__ == "__main__":
    # Journal page URL
    with open(r'inputs.json', 'r') as input_file:
        input_deets = json.load(input_file)

    URL = input_deets['journal_URL']
    directory = input_deets['directory']
    Jname=input_deets['journal_name']
    Chrome_driver=get_driver(directory, URL)
    output=Run(Chrome_driver, Jname, directory)
    output[0].to_excel(directory+"\\"+Jname+"_pivots.xlsx", index=False)
    output[1].to_excel(directory+"\\"+Jname+"_master.xlsx", index=False)
    Chrome_driver.close()