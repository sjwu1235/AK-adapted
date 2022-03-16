import time

from selenium.webdriver.support.ui import WebDriverWait

from connection_controllers.connection_controller import ConnectionController
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

class GenConnectionController(ConnectionController):

    def __init__(self, driver: webdriver, host: str):

        self._driver = driver

        print('Attempting to connect to JSTOR', end = '\r')
        driver.get(host)
        print('\n\nInstructions\n\n')
        print('1. Login to institution')
        print('2. Navigate to home page of jstor')
        print('3. Please accept cookies.')
        print('\n... press Enter once complete to continue\n\n')
        input()
        
        print('\nChecking for successful logon')
        try:
            WebDriverWait(driver, self.DEFAULT_TIMEOUT).until(
                expected_conditions.element_to_be_clickable((By.XPATH, r"//input[@id='query-builder-input']"))
            )
            print("passed")
            time.sleep(5)
        except:
            print("Unable to load search page")
            raise

        
        