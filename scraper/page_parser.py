import requests
from bs4 import BeautifulSoup
import pandas as pd


#can refactor the below function in future

def parse_search_page(response):
    article_titles_list = []
    article_titles = response.select('.link-no-underline')
    for title in article_titles:
        article_titles_list.append(title.text)
        
    article_author_list = []
    article_author = response.select('.contrib')
    for author in article_author:
        article_author_list.append(author.text)
    
    journal = response.select('.metadata') 
    article_journal_name_list = []
    article_volume_list = []
    article_journal_date_list = []
    article_pages_in_journal_list = []
    for article in journal:
        s = article.text
        #get journal date published
        target_date = s.split("(")[1].split(")")[0]
        article_journal_date_list.append(target_date)
        
        #get article journal full name
        target_name = s.split(",")[0]
        article_journal_name_list.append(target_name)
        
        #get article journal volume
        target_volume = s.split(",")[1].split("(")[0]
        article_volume_list.append(target_volume)
        
        #get article pages in journal
        target_pages = str(s.split("),")[1:])
        article_pages_in_journal_list.append(target_pages[2:-2])
        
        
    article_urls = response.select('.pdfLink')
    article_url_list = []
    for url in article_urls:
        s = url['href']
        target_url = s.split("?")[0]
        full_url = 'https://www.jstor.org/' + target_url
        article_url_list.append(full_url)  
        
    articles = pd.DataFrame(list(zip(article_titles_list, article_author_list, article_journal_name_list, article_volume_list ,article_journal_date_list , article_pages_in_journal_list ,  article_url_list)), columns=['Title',"Author",'Journal', 'Journal Volume','Journal Date Published','Article Pages', 'URL'])
    return articles

    
    
