import requests
from bs4 import BeautifulSoup
import pandas as pd


def parse_page(response):
    article_titles_list = []
    article_titles = response.select(".link-no-underline")
    for title in article_titles:
        article_titles_list.append(title.text)

    article_date_pubs = response.select(".metadata")
    article_date_pub_list = []
    for date in article_date_pubs:
        s = date.text
        target_date = s.split("(")[1].split(")")[0]
        article_date_pub_list.append(target_date)

    article_urls = response.select(".pdfLink")
    article_url_list = []
    for url in article_urls:
        s = url["href"]
        target_url = s.split("?")[0]
        full_url = "https://www.jstor.org/" + target_url
        article_url_list.append(full_url)

    articles = pd.DataFrame(
        list(zip(article_titles_list, article_date_pub_list, article_url_list)),
        columns=["Title", "Date Published", "URL"],
    )
    return articles

