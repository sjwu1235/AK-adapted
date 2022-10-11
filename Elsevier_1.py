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

def get_citation(driver, attempt, attempt_limit, directory):
    file_path=[]
    time.sleep(10)
    for x in os.listdir(directory):
        if ('ScienceDirect_citations' in x) and  x[-4:] == ".bib":
            os.remove(directory / x)
    
    if attempt<attempt_limit:
        time.sleep(5)
        
        driver.find_element(By.XPATH, ".//*[@id='article-list']//form//div//div[1]//div//div//p//button[1]//span").click()
        time.sleep(3)

        driver.find_element(By.XPATH, ".//button[@class='button-alternative text-s u-margin-xs-top u-display-block js-export-citations-button button-alternative-primary']//span[2]").click()
        time.sleep(5)
        try:
            WebDriverWait(driver,20).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "js-export-citation-modal-content"))
                )
            driver.find_element(By.XPATH,"//button[@class='button-link button-link-primary u-margin-xs-bottom text-s u-display-block js-citation-type-bibtexabs']//span").click()
            return 1
        except:
            driver.refresh()
            time.sleep(20)
            #recaptcha_check(driver)
            return get_citation(driver, attempt+1, attempt_limit)
    else:
        return 0
        



def process_citation(directory, issue_url):
    file_path=directory / "dummy_dont_exist.txt"    
    final_name=directory / (issue_url.split('https://www.sciencedirect.com/journal/')[-1].replace('/','_')+'.bib')
    if os.path.exists(final_name)==True:
        file_path=final_name
    #poll directory for file existence
    
    while os.path.exists(file_path)==False:
        for x in os.listdir(directory):
            if ('ScienceDirect_citations' in x) and x[-4:] == ".bib":
                file_path = directory / x
                break
            file_path = directory / "dummy_dont_exist.txt"

    fl=None
    with open(file_path, 'r', encoding="UTF-8") as input_file:
        fl = input_file.read()
        if regex.search('A problem occurred trying to deliver text citation data', fl) is not None:
            fl=None     

    if fl is not None:
        fl=fl.replace('\n','').split('@article')
        print(fl)
        data={}
        count=0
        for i in fl[1:]:
            tp=i.find('{')
            tp2=i.find(',')
            test=i[tp2+1:].replace('{','').split('},')
            print(test)
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
        print(pd.DataFrame(data).transpose())
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
    #try:
    #    WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.XPATH, "grid section-container")))
    #    print("passed")
    #except:
    #    print("Failed to access journal page")
    #    driver.refresh()
    #    time.sleep(30)
        #recaptcha_check(driver)
    print('loaded?')
    info_note()
    input()
    time.sleep(20)
    #accept_cookies(driver)
    return driver
    
def get_issue_list(driver, Jname):
    
    data=pd.DataFrame(columns=COLS)
    stop=1
    
    while stop!='stop':
        expansion_errors=0
        click=driver.find_elements(By.XPATH,"//button[@class='accordion-panel-title u-padding-s-ver u-text-left text-l js-accordion-panel-title']")
        #print(click)
        skip=0
        # expand the drawers one by one, sometimes it doesn't work if you bulk click
        # skip first becuase it is auto expanded
        
        for element in click:
            if skip==0:
                skip=skip+1
                continue
            time.sleep(20)
            try:
                element.click() # add in waits to be clickables
            except Exception as e:
                print(e)
                print('problem expanding')
                expansion_errors=expansion_errors+1
    

        # let everything settle
        time.sleep(10)
        print('Please ensure that everything is expanded. Then press enter.')
        print('else reload page and expand all years manually and then continue.')
        print('There are '+str(expansion_errors)+' years that have not been expanded.')
        info_note()
        input()
        decade_List=driver.find_elements(By.XPATH,"//div[@class='issue-item u-margin-s-bottom']")
        for element in decade_List:
            anchor=element.find_element(By.XPATH, ".//a[@class='anchor js-issue-item-link text-m anchor-default']")
            href=anchor.get_attribute('href')
            print(href)
            VI=anchor.text
            MY=element.find_element(By.XPATH, ".//span//h3[@class='js-issue-status text-s']")
            year=MY.text.split(' ')[-1][-5:-1]
            issue_text=MY.text+'__'+VI
            data=pd.concat([data, pd.DataFrame([{'year':int(year),'issue_url':href, 'Elsevier_issue_text':issue_text, 'journal':Jname}])], ignore_index=True )
        print('go to next page')
        info_note()
        stop=input()
    return data


def Run(driver, directory, data):
    throttle=0
    masterlist=pd.DataFrame()
    
    for ind in data.index:   
        time.sleep(5+5*random.random())   
        file_path=directory / (data['issue_url'].iloc[ind].split('https://www.sciencedirect.com/journal/')[-1].replace('/','_')+'.bib')
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

            indicator=get_citation(driver, 0, 10, directory)
            if indicator == 0: 
                print('Unknown problem')
                print('The scraper is going to shut down now.\nPlease restart the scraper')
                driver.close()
                quit()

        masterlist=pd.concat([masterlist, process_citation(directory, data['issue_url'].iloc[ind])], ignore_index=True)
    return masterlist
        
if __name__ == "__main__":
    # Journal page URL
    with open(r'inputs.json', 'r') as input_file:
        input_deets = json.load(input_file)

    #URL = input_deets['journal_URL']
    URL="https://www.sciencedirect.com/journal/journal-of-financial-economics/issues"
    directory = Path(input_deets['directory']) / "journal-of-financial-economics"
    #Jname=input_deets['journal_name']
    #pivots=Path(input_deets['pivots'])
    #masters=Path(input_deets['master'])
    Jname='journal-of-financial-economics'
    Chrome_driver=get_driver(directory, URL)
    pivots=Path("C:/Users/sjwu1/Journal_Data/Extra/JFE_pivots.xlsx") 
    masters=Path("C:/Users/sjwu1/Journal_Data/Extra/JFE_master.xlsx")
    issue_data=None
    x=1
    #if input_deets['pivot_scrape_indicator']==1:
    if x==0:
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