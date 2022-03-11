
from abc import ABC
from random import random
from time import sleep
from math import log

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

def slow_send_keys(self: WebElement, keys: str):
    
    for c in keys:

        n_seconds = -0.1 * log(random())

        sleep(n_seconds)

        self.send_keys(c)

WebElement.slow_send_keys = slow_send_keys   

class ConnectionController(ABC):

    DEFAULT_TIMEOUT = 10

    _driver: webdriver

    def __init__(self, driver: webdriver, host: str, user: str, pw: str):
        self._driver = driver

    def rewrite_url(self, instring: str) -> str:
        return instring

    def get_driver(self) -> webdriver:
        return self._driver