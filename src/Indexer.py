from Storage import BaseStorage
from Requester import Requester
from loguru import logger
from bs4 import BeautifulSoup
from indexer_utils import Indexer_utils

class Indexer(Requester):
    "Indexing a site domain and saving with base-storage"
    def __init__(self, BaseStorage: BaseStorage, DOMAIN=None):
        self.storage = BaseStorage
        if DOMAIN is None:
            DOMAIN = self.get_unindexed_domain()
        self.storage.insert_domain(
            DOMAIN
        )
        self._start_index(DOMAIN)

    def get_unindexed_domain(self):
        query = {"indexed": False}
        result = self.storage.domain_col.find(query).limit(1)
        if result:
            logger.debug(result)
        else:
            logger.debug("Not found any unindexed domain in DB.")

    def get_unindexed_pages(self, domain):
        query = {"domain": domain, "indexed": False}
        result = self.storage.pages_col.find_one(query)
        return result['urls']

    def _start_index(self, DOMAIN):
        self.DOMAIN = DOMAIN
        url = Indexer_utils.domain_to_url(self.DOMAIN)
        if self.storage.pages_col.find({"url": url, "indexed": True}).count() > 0:
            url = self.get_unindexed_pages(self.DOMAIN)
        self.visit_page(url)
        while True:
            url = self.get_unindexed_pages(self.DOMAIN)
            logger.debug(f"unindexed url: {url}")
            if url:
                self.visit_page(url)

    def visit_page(self, url):
        logger.debug(f"visiting page {url}")
        html = self.request(url)
        if html:
            internal_links = Indexer_utils.extract_internal_links(self.DOMAIN, html)
            for link in internal_links:
                if self.storage.pages_col.find({"url": link}).count() <= 0:
                    self.storage.insert_page(url, self.DOMAIN)
        self.storage.pages_col.update_one({"url": url}, { "$set": { "indexed": True } })


