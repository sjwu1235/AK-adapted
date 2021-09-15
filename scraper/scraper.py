from bs4 import BeautifulSoup
import requests 
from http.cookies import SimpleCookie
import re
import bibtexparser
import ast
from typing import Callable
from pathlib import Path

class JstorArticle:
    """This class encapsulates the metadata and actual article downloaded from JSTOR

    Args:
        * meta_dict (dict) : Dictionary of arbitrary metadata key-value pairs
        * pdf (bytes) : Raw bytes of downloaded pdf

    Attributes: 
        metadata_dict (dict) : Direct access to metadata dictionary
    """
    _pdf_blob = None

    metadata_dict = None

    def __init__(self, meta_dict: dict, pdf: bytes) -> None:
        self._pdf_blob = pdf
        self.metadata_dict = meta_dict

    def save_pdf(self, path: Path) -> None:
        """Saves the JstorArticle's pdf data to the given Path

        Args:
            * path (Path): Path object providing location for data to be saved to
        """

        with path.open(OUT_FILE, 'xb') as p:
            p.write(self._pdf_blob)


class JstorScraper:
    """Provides an interface to download an article and its metadata from JSTOR given a valid session

    Args:
        * web_session (requests.Session) : Existing authenticated session (through proxy if needed) to use for scraping JSTOR.
        * rewrite_rule: (Callable[[str], str]) : Optional callable providing a way to rewrite URIs if necessary for proxy etc.
        * base_url (str, optional) : Base URL which requests will be made relative to. Defaults to `https://www.jstor.org`.
        * preview_path (str, optional) : URL relative to base_url for article description/preview. Defaults to `/stable/`.
        * pdf_path (str, optional) : URL relative to base_url for pdf download. Defaults to `/stable/pdf/`.
        * metadata_path (str, optional) : URL relative to base_url for JSON metadata API. Defaults to `/stable/content-metadata/`.
    """

    _session : requests.Session = None

    _rewrite_rule : Callable[[str], str] = None

    _base_url : str = None

    _prev_path : str = None

    _pdf_path : str = None 

    _meta_path : str = None

    def __init__(self, 
                 web_session: requests.Session, 
                 rewrite_rule: Callable[[str], str] = None, 
                 base_url: str = 'https://www.jstor.org',
                 preview_path: str = '/stable/',
                 pdf_path: str = '/stable/pdf/',
                 metadata_path: str = '/stable/content-metadata/') -> None:

        # Populate private attributes:                 

        self._session = web_session

        self._base_url = base_url 

        self._prev_path = preview_path

        self._pdf_path = pdf_path 

        self._meta_path = metadata_path

        # If there is no rewrite rule just use identity function:
        if rewrite_rule == None:
            self._rewrite_rule = lambda m : m
        else:
            self._rewrite_rule = rewrite_rule

    # Loads JSTOR page and finds link to download PDF
    def get_payload_data(self, document_id: int) -> JstorArticle:
        """Obtain download link and metadata for a given article on JSTOR

        Args:
            * document_id (int): The JSTOR document ID to process

        Raises:
            ValueError: If JSTOR returns an unexpected response to requests

        Returns:
            dict: Article metadata and the binary article blob

        """

        view_uri = f'{self._base_url}{self._prev_path}{str(document_id)}'

        print(self._rewrite_rule(view_uri))
        print(self._session.headers)

        # Send the request
        page_request = self._session.get(self._rewrite_rule(view_uri))

        # View response
        if page_request.status_code != 200:
            print(page_request.text)
            raise ValueError(f'Received response code {page_request.status_code}')

        # Build DOM model
        view_page_soup = BeautifulSoup(page_request.content, 'html.parser')

        # Most of the JSTOR page is built dynamically, so there's nothing to scrape directly :'(
        # Try to get document metadata from Google Analytics script block. 
        # TODO: consider adding any missing fields from elsewhere?
        try:
            jstor_metadata_script = view_page_soup.head.find('script', attrs={'data-analytics-provider':'ga'}).string

            jstor_metadata_match = re.search(r'gaData.content = (?P<dict>{[^}]+});', jstor_metadata_script)

            jstor_data_dict = ast.literal_eval(jstor_metadata_match.group('dict'))
        except TypeError as exc:
            raise ValueError('Unable to get document metadata from JSTOR response') from exc

        # Now try download the pdf
        pdf_uri = f'{self._base_url}{self._pdf_path}{str(document_id)}.pdf'

        pdf_request = self._session.get(self._rewrite_rule(pdf_uri))

        # JSTOR may ask us to request terms and conditions - have to send a new request accepting them
        if re.match(r'text/html', pdf_request.headers['content-type']):
            print('wompwomp')

            pdf_page_soup = BeautifulSoup(pdf_request.content, 'html.parser')

            accept_form = pdf_page_soup.find('form', attrs = {'method': 'POST', 'action': re.compile(r'/tc/verify')})

            csrf_token = accept_form.find('input', attrs = {'name': 'csrfmiddlewaretoken'})['value']

            pdf_request_payload = {'csrfmiddlewaretoken' : csrf_token}

            # Update URI according to action from prior request
            pdf_uri = f'{self._base_url}{accept_form["action"]}'

            print(pdf_uri)

            pdf_request = self._session.post(self._rewrite_rule(pdf_uri), data = pdf_request_payload)

        # Do a final check that we have apparently received a pdf as expected.
        if pdf_request.headers['content-type'] != 'application/pdf':
            raise ValueError('JSTOR did not return a pdf when expected - got response MIME content type of ' + pdf_request.headers['content-type'])

        return JstorArticle(jstor_data_dict, pdf_request.content)