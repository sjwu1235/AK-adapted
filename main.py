from scraper.scraper import JstorScraper
import requests
import scraper
import re
from pathlib import Path

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'

PAPER_ID = '2629139'

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

def uct_rewrite(instring: str) -> str:
    # Hopefully this regex will handle most real-world cases that we need
    url_regex = re.compile(r'(?P<proto>https?)://(?P<host>[-A-Za-z.]+)(?P<port>:[0-9]+)?(?P<pathqry>/.+)?')

    url_match = url_regex.fullmatch(instring)

    if url_match == None or url_match['host'] == None: 
        raise ValueError('instring does not appear to be a useable URL')

    # Generating rewritten string using string interpolation
    retval = f'https://{url_match["host"].replace(".", "-")}.ezproxy.uct.ac.za{str(url_match["port"] or "")}{str(url_match["pathqry"] or "")}'

    return retval

# --------------------------------------------------
# Code that runs test: 

#print(uct_rewrite(test_uri))

with open(r'cookiefile.txt', 'r') as cookiedata:

    cookietext = cookiedata.readline()

cookies = parse_cookies(cookietext)

#print(cookies)

session = requests.Session()

with session as s:

    s.headers['User-Agent'] = USER_AGENT

    s.cookies.update(cookies)

    print(s.cookies)

    the_scraper = JstorScraper(s, uct_rewrite)

    initreq = the_scraper.get_payload_data(PAPER_ID)

    initreq.save_pdf(Path(OUT_FILE))