from selenium.common.exceptions import TimeoutException
import re

from math import log
from random import random
from time import sleep
from pathlib import Path

import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from connection_controllers.connection_controller import ConnectionController

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'     

class DownloadException(Exception):
    pass


class SearchResponse:
    doi: str
    url: str
    docid: str

    def __init__(self, doi, url):
        self.doi = doi
        self.url = url
        self.docid = re.sub(
            r'/stable/(?:pdf/)?(?P<id>[a-z0-9]+)\.[a-z0-9]{1,4}(?:\?.+)?', 
            r'\g<id>',
            url
        )

    def __str__(self):
        return f'SearchResponse Object: {{ Article ID: {self.docid}; DOI: {self.doi}; URL: {self.url} }}'

    def __repr__(self):
        return f"SearchResponse('{self.doi}', '{self.url}')"

class JstorArticle:
    """This class encapsulates the metadata and actual article downloaded from JSTOR

    Args:
        * meta_dict (str) : String representation of JSON object with arbitrary metadata key-value pairs
        * pdf (bytes) : Raw bytes of downloaded pdf
        * _pdf_id (int): DOI of paper 

    Attributes: 
        metadata_json (str) : Direct access to metadata JSON object
    """
    _pdf_blob : bytes = None

    metadata_json : str = None
    
    _pdf_id : int = None 

    def __init__(self, meta_json: str, pdf: bytes, pdf_id: int) -> None:
        self._pdf_blob = pdf
        self.metadata_json = meta_json
        self._pdf_id = pdf_id

    def save_pdf(self, path: Path) -> None:
        """Saves the JstorArticle's pdf data to the given Path

        Args:
            * path (Path): Path object providing location for data to be saved to
        """

        with path.open(path, 'xb') as p:
            p.write(self._pdf_blob)


class JstorScraper:
    """Provides an interface to download an article and its metadata from JSTOR given a valid session

    Args:
        * controller (ConnectionController) : Existing authenticated ConnectionController instance 
        * base_url (str, optional) : Base URL which requests will be made relative to. Defaults to `https://www.jstor.org`.
        * preview_path (str, optional) : URL relative to base_url for article description/preview. Defaults to `/stable/`.
        * pdf_path (str, optional) : URL relative to base_url for pdf download. Defaults to `/stable/pdf/`.
        * metadata_path (str, optional) : URL relative to base_url for JSON metadata API. Defaults to `/stable/content-metadata/`.
        * mean_request_delay_s (int, optional) : Mean wait time between requests. 
            These will follow an exponential distribution with mean equal to this value. Defaults to 15.
        * log_level (int, optional) : Controls the amount of output printed. Defaults to 1. Options are
            - 0: No output 
            - 1: Status updates
            - 2: Full request logging (not yet implemented)
            - 3: Verbose logging (not yet implemented)
    """

    _base_url : str = None

    _prev_path : str = None

    _pdf_path : str = None 

    _meta_path : str = None

    _mean_wait_time_s : int = 10

    _log_level : int = 1

    _controller: ConnectionController = None

    _driver: webdriver

    def __init__(self, 
                 controller: ConnectionController, 
                 base_url: str = 'https://www.jstor.org',
                 preview_path: str = '/stable/',
                 pdf_path: str = '/stable/pdf/',
                 metadata_path: str = '/stable/content-metadata/',
                 mean_request_delay_s: int = 10,
                 log_level = 1) -> None:

        # Populate private attributes:                

        self._base_url = base_url 

        self._prev_path = preview_path

        self._pdf_path = pdf_path 

        self._meta_path = metadata_path

        self._mean_wait_time_s = mean_request_delay_s

        self._log_level = log_level

        self._controller = controller

        self._driver = controller.get_driver()

    def _wait_before_request(self):

        if random() < 0.34:
            self._driver.execute_script(f'window.scrollBy({{ top: {round(random() * 10 )} * window.innerHeight / 20, left: 0, behavior: "smooth" }})')

        n_seconds = -self._mean_wait_time_s * log(random())

        if self._log_level > 0:
            print(f'Waiting {n_seconds:.1f}s before next request', end = '\r')

        sleep(n_seconds)

    def _parse_search_page_lite(self, response: BeautifulSoup) -> 'list[SearchResponse]':

        results_list: 'list[SearchResponse]' = []

        results_list = [
            SearchResponse(
                dl_button['data-doi'],
                dl_button['href']
            ) 
                for dl_button in response.select('.pdfLink') 
                if 'href' in dl_button.attrs and 'data-doi' in dl_button.attrs
            ]
        
        return results_list    
        
    def get_search_results(self, journal_name: str, request_timeout: int=10):
        """Obtain metadata and download links for articles a given journal name and number of articles
        
        Args:  
            * journal_name (str): The name of the journal to search 
            * request_timeout (int, optional): Length of time to wait 
             for requests to successfully complete

             
        Raises:
            ValueError: If JSTOR returns an unexpected response to requests
            
        Returns:
            dataframe: Articles metadata 
        
        """
        view_uri = self._controller.rewrite_url(f'{self._base_url}')
        
        journal = "pt:("+ journal_name + ")"

        # If session just started we will already be on landing page, so don't reload it.
        # Now try scrape the webpage 
        # First fill out search bar then find download button search

        search_bar = self._driver.find_element_by_xpath(".//input[@id='query-builder-input']")
        search_button = self._driver.find_element_by_xpath(".//button[@title='search button']")
        
        # If we can't find the search bar we can try load instead
        if search_bar == None or search_button == None:

            if self._log_level > 0:
                print(f'Performing GET request for search landing page at {view_uri}', end = '\r')
            #page_request = self._session.get(view_uri)
            
            # Send the request
            self._wait_before_request()
            self._driver.get(view_uri)

            try:
                WebDriverWait(self._driver, 5).until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, ".//input[@id='query-builder-input'")
                    )
                )
            except TimeoutException as e:
                raise TimeoutException("Seem to be unable to load JSTOR landing page") from e


            # And now try again...
            search_bar = self._driver.find_element_by_xpath(".//input[@id='query-builder-input']")
            search_button = self._driver.find_element_by_xpath(".//button[@title='search button']")

            # If they're still not around we have a problem.
            if search_bar == None or search_button == None:
                raise Exception("Unable to find search elements on JSTOR landing page")
        

        self._wait_before_request()
        search_bar.slow_send_keys(journal) 
        search_button.click()

        try:
            WebDriverWait(self._driver, 10).until(
                expected_conditions.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//a[@class = "link-no-underline" and @data-itemtype]'
                    )
                )
            )
        except TimeoutException as e:
            raise TimeoutException("Search results didn't load within expected timeframe") from e
            
        soup = BeautifulSoup(self._driver.page_source, 'html.parser')
        articles = self._parse_search_page_lite(soup)
        
        return articles
        
    # Loads JSTOR page and finds link to download PDF
    def get_payload_data(self, document_id: str, request_timeout: int = 10) -> JstorArticle:
        """Obtain download link and metadata for a given article on JSTOR

        Args:
            * document_id (int): The JSTOR document ID to process
            * request_timeout (int, optional): Length of time to wait 
              for requests to successfully complete

        Raises:
            ValueError: If JSTOR returns an unexpected response to requests

        Returns:
            dict: Article metadata and the binary article blob

        """

        view_uri = self._controller.rewrite_url(f'{self._base_url}{self._prev_path}{document_id}')

        # Send the request
        self._wait_before_request()

        if self._log_level > 0:
            print(f'Performing GET request for article landing page at {view_uri}', end = '\r')
        #page_request = self._session.get(view_uri)
        self._driver.get(view_uri)

        # Load article landing page
        try:
            WebDriverWait(self._driver, request_timeout).until(
                expected_conditions.visibility_of_element_located((By.ID, 'page-scan-info'))
            )
        except:
            print('Unable to load article landing page')
            raise

        # Pull article metadata from DOM
        # JSTOR (currently) use vuejs framework
        # We can use that to pull what the page already downloaded.
        # This should make activity more human-like
        metadata = self._driver.execute_script(
            '''return document.
                        getElementById('page-scan-info').
                        __vue__.$store.state.
                        content.contentData;'''
            )

        # Now try download the pdf
        # First find download button and download link
        pdf_button = self._driver.find_element_by_xpath('//a[@data-qa="download-pdf"]')
        pdf_path = pdf_button.get_attribute('href')

        # Get T&C state
        tc_state = self._driver.execute_script(
            '''return document.
                        getElementsByClassName('page-scan-info')[0].
                        __vue__.$store.state.
                        user.termsAndConditionsAccepted;'''
            )

        self._wait_before_request()

        pdf_button.click()

        # Get handle to current set of tabs
        tab_list = self._driver.window_handles
        # num_tabs = len(tab_list)
        cur_tab = self._driver.current_window_handle

        # If T&C haven't already been accepted, modal will show up:
        if not tc_state:
            accept_button = self._driver.find_element_by_xpath('//pharos-button[@data-qa="accept-terms-and-conditions-button"]')

            self._wait_before_request()

            accept_button.click()

        # Now it will try to open new tab with pdf.
        try:
            WebDriverWait(self._driver, 5).until(
                expected_conditions.new_window_is_opened(tab_list)
            )
        except TimeoutException as e:
            raise TimeoutException("Didn't detect a pdf window opening") from e

        new_tabs = self._driver.window_handles    

        for nt in new_tabs:
            if not (nt in tab_list):
                self._driver.switch_to.window(nt)

                self._driver.close()

                self._driver.switch_to.window(cur_tab)

                break

        # Close the new tab 
        # We will try rather use requests to download the pdf otherwise no way to save
        #self._driver.close()

        # Make sure we are back on the original tab
        #self._driver.switch_to.window(cur_tab)

        # Get cookies to use for requests
        selenium_cookies = self._driver.get_cookies()

        new_cookies = {c['name']:c['value'] for c in selenium_cookies}

        session = requests.Session()

        with session as s:

            s.headers['User-Agent'] = USER_AGENT

            s.cookies.update(new_cookies)

            pdf_request = s.get(pdf_path)

        if pdf_request.status_code != 200:
            raise DownloadException(f'''Could not successfully download PDF
                                               Status code was {pdf_request.status_code}
                                            ''')
        if pdf_request.headers['content-type'] != 'application/pdf':
            raise DownloadException(f'''Could not successfully download PDF
                                               Response content-type was {pdf_request.headers['content-type']}
                                            ''')

        return JstorArticle(metadata, pdf_request.content)

    
    # Loads JSTOR pages and finds link to download PDF
    def get_multi_payload_data(self, document_ids: 'list[str]', request_timeout: int = 25)-> JstorArticle: 
        """Obtain download link and metadata for a given article on JSTOR

        Args:
            * document_ids (int list/array): The JSTOR document IDs to process
            * request_timeout (int, optional): Length of time to wait 
              for requests to successfully complete

        Raises:
            ValueError: If JSTOR returns an unexpected response to requests

        Returns:
            dict: Article metadata and the binary article blob for article list 

        """
        lst = []
        for id in document_ids:
            view_uri = self._controller.rewrite_url(f'{self._base_url}{self._prev_path}{id}')

            # Send the request
            self._wait_before_request()
    
            if self._log_level > 0:
                print(f'Performing GET request for article landing page at {view_uri}', end = '\r')
            #page_request = self._session.get(view_uri)
            self._driver.get(view_uri)
    
            # Load article landing page
            try:
                WebDriverWait(self._driver, request_timeout).until(
                    expected_conditions.visibility_of_element_located((By.ID, 'item_view_content'))
                )
            except:
                print('Unable to load article landing page')
                raise
    
            # Pull article metadata from DOM
            # JSTOR (currently) use vuejs framework
            # We can use that to pull what the page already downloaded.
            # This should make activity more human-like
            metadata = self._driver.execute_script(
                '''return document.
                            getElementsByClassName('abstract-container')[0].
                            __vue__.$store.state.
                            content.contentData;'''
                )
    
            # Now try download the pdf
            # First find download button and download link
            pdf_button = self._driver.find_element_by_xpath('//a[@data-qa="download-pdf"]')
            pdf_path = pdf_button.get_attribute('href')
    
            # Get T&C state
            tc_state = self._driver.execute_script(
                '''return document.
                            getElementsByClassName('abstract-container')[0].
                            __vue__.$store.state.
                            user.termsAndConditionsAccepted;'''
                )
    
            self._wait_before_request()
    
            pdf_button.click()
    
            # Get handle to current set of tabs
            tab_list = self._driver.window_handles
            num_tabs = len(tab_list)
            cur_tab = self._driver.current_window_handle
    
            # If T&C haven't already been accepted, modal will show up:
            if not tc_state:
                accept_button = self._driver.find_element_by_xpath('//pharos-button[@data-qa="accept-terms-and-conditions-button"]')
    
                self._wait_before_request()
    
                accept_button.click()
    
            try:
                WebDriverWait(self._driver, 5).until(
                    expected_conditions.new_window_is_opened(tab_list)
                )
            except TimeoutException as e:
                raise TimeoutException("Didn't detect a pdf window opening") from e

            new_tabs = self._driver.window_handles    

            for nt in new_tabs:
                if not (nt in tab_list):
                    self._driver.switch_to.window(nt)

                    self._driver.close()

                    self._driver.switch_to.window(cur_tab)

                    break

            # Close the new tab 
            # We will try rather use requests to download the pdf otherwise no way to save
            #self._driver.close()

            # Make sure we are back on the original tab
            #self._driver.switch_to.window(cur_tab)

            # Get cookies to use for requests
            selenium_cookies = self._driver.get_cookies()

            new_cookies = {c['name']:c['value'] for c in selenium_cookies}

            session = requests.Session()

            with session as s:

                s.headers['User-Agent'] = USER_AGENT

                s.cookies.update(new_cookies)

                pdf_request = s.get(pdf_path)

            if pdf_request.status_code != 200:
                raise DownloadException(f'''Could not successfully download PDF
                                                Status code was {pdf_request.status_code}
                                                ''')
            if pdf_request.headers['content-type'] != 'application/pdf':
                raise DownloadException(f'''Could not successfully download PDF
                                                Response content-type was {pdf_request.headers['content-type']}
                                                ''')
            print(id)
            lst.append(JstorArticle(metadata, pdf_request.content,id))
                                            
       
        return lst
