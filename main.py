
import re
import json
from pathlib import Path
from typing import Callable

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from webdriver_manager.chrome import ChromeDriverManager

import scraper
from scraper.scraper import JstorScraper
from bs4 import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'

PAPER_ID = '2629139'

OUT_FILE = r'F:\woo.pdf'

DEFAULT_TIMEOUT = 10

# Converts a request's cookie string into a dictionary that we can use with requests.
def parse_cookies(cookiestring: str) -> dict:

    # The UCT session cookies have messy formats that http.cookies doesn't like
    # We have to manually parse - this may be fragile!

    cookies = {}
    kv_regex = re.compile(r'(?P<key>[^;=]+)=(?P<val>[^;]*);')
    
    for c in kv_regex.finditer(cookiestring):
        cookies[c.group('key')] = c.group('val')

    return cookies

def uct_rewrite(instring: str) -> str:
    # Hopefully this regex will handle most real-world cases that we need
    url_regex = re.compile(r'(?P<proto>https?)://(?P<host>[-A-Za-z.]+)(?P<port>:[0-9]+)?(?P<pathqry>/.+)?')

    url_match = url_regex.fullmatch(instring)

    if url_match == None or url_match['host'] == None: 
        raise ValueError('instring does not appear to be a useable URL')

    # Generating rewritten string using string interpolation
    retval = f'https://{url_match["host"].replace(".", "-")}.ezproxy.uct.ac.za{str(url_match["port"] or "")}{str(url_match["pathqry"] or "")}'

    return retval

def init_session(driver: webdriver, host: str, user: str, pw: str, rewrite_rule: Callable[[str], str]) -> None:
    print('Attempting to connect to JSTOR', end = '\r')
    driver.get(rewrite_rule(host))

    # Wait until inputs have loaded
    print('Waiting for logon page to load', end = '\r')
    try:
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            expected_conditions.presence_of_element_located((By.ID, 'userNameInput'))
        ) 
    except:
        print("waaah")
        raise

    # Send login info
    print('Requesting logon details', end = '\r')
    driver.find_element_by_xpath(r".//input[@id='userNameInput']").send_keys(user)
    driver.find_element_by_xpath(r".//input[@id='passwordInput']").send_keys(pw)
    driver.find_element_by_xpath(r".//span[@id='submitButton']").click()
    
    print('Checking for successful logon', end = '\r')
    try:
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            expected_conditions.element_to_be_clickable((By.XPATH, r"//button[@data-sc='but click:search']"))
        )
    except:
        print("waah2")
        raise

    return driver




# --------------------------------------------------
# Code that runs test: 

#print(uct_rewrite(test_uri))



chrome_options = webdriver.ChromeOptions()
# ------ #
# uncomment the below if you dont want the google chrome browser UI to show up.

#chrome_options.add_argument('--headless')

#chrome_options.add_argument(f'user-agent={USER_AGENT}')

#with open(r'uctpw.json', 'r') as logon_file:

#    logon_deets = json.load(logon_file)

#web_session = init_session(webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options),
#                            'https://www.jstor.org',
#                            logon_deets['user'],
#                            logon_deets['pass'],
#                            uct_rewrite)

#the_scraper = JstorScraper(web_session, uct_rewrite)

#articles = the_scraper.get_search_results(journal_name="Econometrica")

with open(r'testhtml.html', 'r', encoding='utf-8') as testhtml:

    test_html = BeautifulSoup(testhtml.read(), 'html.parser')

articles = JstorScraper._parse_search_page_lite(test_html)

print(articles[0])


#test=the_scraper.get_multi_payload_data(document_ids={1,2,3,4,5,5,7,8,4,2})

#initreq = the_scraper.get_payload_data(PAPER_ID)

#initreq.save_pdf(Path(OUT_FILE))

