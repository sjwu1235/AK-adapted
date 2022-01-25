import json
from pathlib import Path
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from connection_controllers.uct_connection_controller import UctConnectionController


with open(r'inputs.json', 'r') as input_file:
    input_deets = json.load(input_file)

# Journal page URL
URL = input_deets['journal_URL']
directory = input_deets['directory']

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.
# not reccommended
#chrome_options.add_argument('--headless')

chrome_options.add_argument(f'user-agent={USER_AGENT}')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_extension('./extension_1_38_6_0.crx')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option('prefs', {
    "download.default_directory": directory, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True, #It will not show PDF directly in chrome
    "credentials_enable_service": False, # gets rid of password saver popup
    "profile.password_manager_enabled": False #gets rid of password saver popup
})

driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

with open(r'uctpw.json', 'r') as logon_file:
    logon_deets = json.load(logon_file)

web_session = UctConnectionController(driver, 
                                      'https://www.jstor.org',
                                      logon_deets['user'],
                                      logon_deets['pass'])

driver.get(URL)

WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "facets-container")))

cols=['year', 'month', 'volume', 'issue','issue_url','Jstor_issue_text','journal', 'pivot_url', 'no_docs']
data=pd.DataFrame(columns=cols)

click=driver.find_elements_by_xpath(r".//dl[@class='facet accordion']//dl//dt//a")
# expand the drawers one by one, sometimes it doesn't work if you bulk click
for element in click:
    time.sleep(5)
    element.click()
# let everything settle
time.sleep(10)

decade_List=driver.find_elements_by_xpath(r".//dd//ul//li")

for element in decade_List:
    year_list=element.find_elements_by_xpath(r".//ul//li//a")
    temp=element.get_attribute('data-year')
    if temp==None:
        continue
    print(temp)
    for item in year_list:
        uct_stable_url=item.get_attribute('href')
        Jstor_issue_text=item.text
        data=data.append(pd.Series([int(temp), None, None, None, uct_stable_url, Jstor_issue_text, 'AER', None, None], index=data.columns), ignore_index=True )

for ind in data.index:   
    time.sleep(1)     
    driver.get(data['issue_url'][ind])
    try:
        WebDriverWait(driver,20).until(expected_conditions.presence_of_element_located((By.ID, "bulk_citation_export_form")))
    except:
        print("Timed out: manually resolve the page to "+data['issue_url'][ind])
        print("Press enter to continue after page completely loads")
        input()

    data['pivot_url'][ind]=driver.find_element_by_xpath(r".//div[@class='media-body media-object-section main-section']//div[@class='stable']").text
    all_urls=driver.find_elements_by_xpath(r".//div[@class='media-body media-object-section main-section']//div[@class='stable']")
    data['no_docs'][ind]=len(all_urls)
    issue_data=driver.find_element_by_xpath(r".//h1//div[@class='issue']").text.split(',')
    print(issue_data)
    print(len(all_urls))
    data['volume'][ind]=int(issue_data[0].split()[1])
    try:
        data['issue'][ind]=issue_data[1].split()[1].replace('/','-')
        data['month'][ind]=issue_data[2].split()[0]
    except:
        print('No issue or month metadata. Possibly is supplement, index or special issue')

data.to_excel(input_deets['pivots'], index=False)
