import json
from pathlib import Path
from re import L
import time
import pandas as pd
import random
import os
from plyer import notification
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import regex

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
COLS = ['year','issue_url','Elsevier_issue_text','journal']


# Elsevier approach
# Can use the same processor for citations as jstor through bibtex file structure. NB: file extension is .bib
# Req: find linking id between pivot list and bulk citations file. URL is straight forward on elsevier. Can use Y-V-I-part because sometimes has part A and part B. else use last part of url replacing backslash with _
# Req: Traversal issue. will require user to look at multiple page loads for pivot list generation.
# By default, the first year of list drawer opens. Req check for openess of drawer before expansion. 
# TBH, doesn't seem to matter if drawers expand so long as drawer items are correctly loaded.
# Req: Check if citations on scopus match or not. and if scopus is exhaustive on the same citations list else bulk download is simple.
# Bulk citations download file naming is not detereministic. Seems to be time based.
# Req: check for author scopus id or other information per article that might be available on article page.
# Req + Risk: naming paradigm for article ids are the same as jstor. Or worse, no naming paradigm at all. will req rename with prefix.
# in bulk download: Naming paradigm uses first X amount of letters from title that will uniquely id each article + journal name as suffix
# in page by page download: uses DOI or URL ref.
# https://stackoverflow.com/questions/3451111/unzipping-files-in-python for processing zip files, use shutil method because it will work with path lib object
# bulk citations download with time stamp. need glob or glob2 module https://stackoverflow.com/questions/4296138/use-wildcard-with-os-path-isfile
# https://stackoverflow.com/questions/59109010/using-wildcards-in-pathlib 
def info_note():
    notification.notify(
        app_name='Elsevier.py',
        title = "Confirm Stuff",
        message="There is something you need to do on the scraper" ,
        ticker='Help!',
        timeout=30)

def get_zip(driver, attempt, attempt_limit, directory):
    time.sleep(10)
    for x in os.listdir(directory):
        if ('ScienceDirect_articles' in x) and  x[-4:] == ".zip":
            os.remove(directory / x)
    
    if attempt<attempt_limit:
        time.sleep(5)
        
        driver.find_element(By.XPATH, ".//*[@id='article-list']//form//div//div[1]//div//div//p//button[1]//span").click()
        time.sleep(3)

        #driver.find_element(By.XPATH, ".//*button[@class='button-alternative text-s button-alt-overide']//span[2]").click()
        driver.find_element(By.XPATH, ".//*[@id='article-list']/form/div/div[1]/div/div/button[1]/span[2]").click()
        time.sleep(5)
        #return int(driver.find_element(By.XPATH, ".//html//body//div[7]//div//div//div//div//p//span//strong").text)
        try:
            driver.find_element(By.XPATH,".//html//body//div[7]//div//div//div//div//h1").text
            return 0
        except:
            return 1
        #//*[@id="article-list"]/form/div/div[1]/div/div/button[1]/span[2]
        #try:
        #    WebDriverWait(driver,20).until(
        #        expected_conditions.presence_of_element_located((By.XPATH,"//button[@class='button modal-close-button button-anchor move-right move-top u-margin-s size-xs']//span"))
        #        )
                
        #    driver.find_element(By.XPATH,"//button[@class='button modal-close-button button-anchor move-right move-top u-margin-s size-xs']//span").click()
        #    return 1
        #except:
        #    driver.refresh()
        #    time.sleep(20)
            #recaptcha_check(driver)
        #    return get_zip(driver, attempt+1, attempt_limit)
    else:
        return 0

def process_zip(directory, issue_url):
    file_path=directory / "dummy_dont_exist.txt"    
    final_name=directory / (issue_url.split('https://www.sciencedirect.com/journal/')[-1].replace('/','_')+'.zip')
    if os.path.exists(final_name)==True:
        file_path=final_name
    #poll directory for file existence
    
    while os.path.exists(file_path)==False:
        for x in os.listdir(directory):
            if ('ScienceDirect_articles' in x) and x[-4:] == ".zip":
                file_path = directory / x
                fl=1
                break
            file_path = directory / "dummy_dont_exist.txt"
        time.sleep(10)

     

    if fl is not None:
        print('rename files')
        os.rename(file_path, final_name)
        return 1
    else:
        print("Zip did not load correctly. Citation file for "+issue_url+" will be deleted. This will be re-downloaded next session. ")
        if os.path.exists(file_path)==True:
            os.remove(file_path)
        return 0

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
    #driver.set_window_position(1024, 1024, windowHandle ='current')
    driver.get(URL)
    try:
        WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.XPATH, "grid section-container")))
        print("passed")
    except:
        print("Failed to access journal page")
        driver.refresh()
        time.sleep(30)
        #recaptcha_check(driver)
    print('loaded?')
    #info_note()
    input()
    time.sleep(20)
    #accept_cookies(driver)
    return driver

def Run(driver, directory, data):
    throttle=0
    masterlist=pd.DataFrame()
    
    for ind in data.index:   
        
        file_path=directory / (data['issue_url'].iloc[ind].split('https://www.sciencedirect.com/journal/')[-1].replace('/','_')+'.zip')
        print(file_path)
        #poll directory for file existence
        if os.path.exists(file_path)==False:
            driver.get(data['issue_url'].iloc[ind])
            try:
                WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "article-list")))
            except:
                print("Timed out: manually resolve the page to "+ data['issue_url'].iloc[ind])
                print("Press enter to continue after page completely loads")
                #recaptcha_note()
                input()
                #recaptcha_check(driver)
                
            time.sleep(5+throttle)
            #accept_cookies(driver)     

            indicator=get_zip(driver, 0, 10, directory)
            if indicator == 0: 
                print('Unknown problem')
                print('The scraper is going to shut down now.\nPlease restart the scraper')
                driver.close()
                quit()
            process_zip(directory, data['issue_url'].iloc[ind])
            time.sleep(5+5*random.random())   
    return masterlist
        
if __name__ == "__main__":
    # Journal page URL
    with open(r'inputs.json', 'r') as input_file:
        input_deets = json.load(input_file)

    #URL = input_deets['journal_URL']
    URL="https://www.sciencedirect.com/"
    directory = Path(input_deets['directory']) / "journal-of-financial-economics"
    #Jname=input_deets['journal_name']
    #pivots=Path(input_deets['pivots'])
    #masters=Path(input_deets['master'])
    StartYear=1983
    EndYear=1988
    Jname='journal-of-financial-economics'
    Chrome_driver=get_driver(directory, URL)
    pivots=Path("D:/docs/Masters/Data/Extra/JFE_pivots.xlsx") 
    masters=Path("D:/docs/Masters/Data/Extra/JFE_master.xlsx")
    issue_data=pd.read_excel(pivots)
    issue_data_subset=issue_data[(issue_data['year']>=StartYear)&(issue_data['year']<=EndYear)].reset_index(drop=True)
    output=Run(Chrome_driver, directory, issue_data)
    Chrome_driver.close()