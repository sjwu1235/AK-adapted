
import re

from selenium.webdriver.support.ui import WebDriverWait

from connection_controllers.connection_controller import ConnectionController
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

class UctConnectionController(ConnectionController):

    def rewrite_url(self, instring: str) -> str:
    # Hopefully this regex will handle most real-world cases that we need
        url_regex = re.compile(r'(?P<proto>https?)://(?P<host>[-A-Za-z.]+)(?P<port>:[0-9]+)?(?P<pathqry>/.+)?')

        url_match = url_regex.fullmatch(instring)

        if url_match == None or url_match['host'] == None: 
            raise ValueError('instring does not appear to be a useable URL')

        # Generating rewritten string using string interpolation
        retval = f'https://{url_match["host"].replace(".", "-")}.ezproxy.uct.ac.za{str(url_match["port"] or "")}{str(url_match["pathqry"] or "")}'

        return retval

    def __init__(self, driver: webdriver, host: str, user: str, pw: str):

        self._driver = driver

        print('Attempting to connect to JSTOR', end = '\r')
        driver.get(self.rewrite_url(host))

        # Wait until inputs have loaded
        print('Waiting for logon page to load', end = '\r')
        try:
            WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                expected_conditions.presence_of_element_located((By.ID, 'userNameInput'))
            ) 
        except:
            print("Expected logon page was not found")
            raise

        # Send login info
        print('Requesting logon details', end = '\r')
        driver.find_element_by_xpath(r".//input[@id='userNameInput']").send_keys(user)
        driver.find_element_by_xpath(r".//input[@id='passwordInput']").send_keys(pw)
        driver.find_element_by_xpath(r".//span[@id='submitButton']").click()
        
        print('Checking for successful logon', end = '\r')
        try:
            WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                expected_conditions.element_to_be_clickable((By.XPATH, r"//button[@data-sc='but click:search']"))
            )
        except:
            print("Unable to load search page")
            raise
