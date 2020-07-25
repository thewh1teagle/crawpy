from bs4 import BeautifulSoup
from Storage import BaseStorage

class Scraper(BaseStorage):
    "Asking base-storage for non scraped urls, scraping the content and sending to storage"
    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html, features='html.parser')
        
