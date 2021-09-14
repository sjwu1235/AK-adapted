from bs4 import BeautifulSoup
import requests 
from http.cookies import SimpleCookie
import re
import bibtexparser
import ast

BASE_HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'})
BASE_URL = 'https://www-jstor-org.ezproxy.uct.ac.za/'

VIEW_ONLINE_PATH = 'https://www-jstor-org.ezproxy.uct.ac.za/stable/'
PDF_PATH = 'https://www-jstor-org.ezproxy.uct.ac.za/stable/pdf/'

PAPER_ID = '2629139'

AUTH_COOKIE = ''

OUT_FILE = r'F:\woo.pdf'



# Converts a request's cookie string into a dictionary that we can use with requests.
def parse_cookies(cookiestring: str) -> dict:

    # The UCT session cookies have messy formats that http.cookies doesn't like
    # We have to manually parse - this may be fragile!

    cookies = {}
    kv_regex = re.compile(r'(?P<key>[^;=]+)=(?P<val>[^;]*);')
    
    for c in kv_regex.finditer(cookiestring):
        cookies[c.group('key')] = c.group('val')

    return cookies

# Loads JSTOR page and finds link to download PDF
def get_payload_data(document_id: int, session: requests.Session) -> dict:

    view_uri = VIEW_ONLINE_PATH + str(document_id)

    # Send the request
    page_request = session.get(view_uri, headers = BASE_HEADERS)

    # View response
    if page_request.status_code != 200:
        raise ValueError('Received response code ' + page_request.response_code)

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
    pdf_uri = PDF_PATH + str(document_id) + '.pdf'

    pdf_request = session.get(pdf_uri, headers = BASE_HEADERS)

    # JSTOR may ask us to request terms and conditions - have to send a new request accepting them
    if pdf_request.headers['content-type'] == 'text/html':
        pdf_page_soup = BeautifulSoup(pdf_request.content, 'html.parser')

        accept_form = pdf_page_soup.find('form', attrs = {'method': 'POST', 'action': re.compile(r'/tc/verify')})

        csrf_token = accept_form.find('input', attrs = {'name': 'csrfmiddlewaretoken'})['value']

        pdf_request_payload = {'csrfmiddlewaretoken' : csrf_token}

        pdf_request = session.post(BASE_URL + accept_form['action'], data = pdf_request_payload)

    # Do a final check that we have apparently received a pdf as expected.
    if pdf_request.headers['content-type'] != 'application/pdf':
        raise ValueError('JSTOR did not return a pdf when expected - got response MIME content type of ' + pdf_request.headers['content-type'])

    jstor_data_dict['blob'] = pdf_request.content

    return jstor_data_dict

# --------------------------------------------------
# Code that runs test:

test_uri = ''    

cookies = parse_cookies(AUTH_COOKIE)

session = requests.Session()

session.cookies.update(cookies)

initreq = get_payload_data(PAPER_ID, session)

outfile = open(OUT_FILE, 'xb')

outfile.write(initreq['blob'])

outfile.close()

session.close()