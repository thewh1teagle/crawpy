from Storage import BaseStorage
from Requester import Requester
from loguru import logger
from bs4 import BeautifulSoup
from indexer_utils import Indexer_utils
from time import sleep

class Indexer(Requester):
    "Indexing a site domain and saving with base-storage"
    def __init__(self, BaseStorage: BaseStorage, DOMAIN=None, max_depth=2):
        self.storage = BaseStorage
        if DOMAIN is None:
            DOMAIN = self.storage.get_unindexed_domain()
        self.storage.insert_domain(
            DOMAIN
        )
        self.DEPTH = 0
        self.MAX_DEPTH = max_depth
        self._start_index(DOMAIN)

    
 
    def _start_index(self, DOMAIN):
        self.DOMAIN = DOMAIN
        url = Indexer_utils.domain_to_url(self.DOMAIN)
        if self.storage.pages_col.find({"url": url, "indexed": True}).count() > 0:
            url = self.storage.get_unindexed_page(self.DOMAIN, self.MAX_DEPTH)
        self.visit_page(url)
        while True:
            url = self.storage.get_unindexed_page(self.DOMAIN, self.MAX_DEPTH)
            logger.debug(f"unindexed url: {url}")
            if url:
                self.visit_page(url['url'])

    def visit_page(self, url):
        logger.debug(f"visiting page {url}")
        html = self.request(url)
        if html:
            internal_links = Indexer_utils.extract_internal_links(self.DOMAIN, html, url)
            for link in internal_links:
                logger.debug(f"iter link: {link}")
                self.storage.insert_page(link, self.DOMAIN, self.DEPTH)
        self.storage.pages_col.update_one({"url": url}, { "$set": { "indexed": True } })


