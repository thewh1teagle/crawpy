from .Storage import BaseStorage
from .requester import Requester
from loguru import logger
from .utils import indexerutils
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread

class Indexer(Requester):
    "Indexing a site domain and saving with base-storage"
    def __init__(self, BaseStorage: BaseStorage, DOMAIN=None, max_depth=2, workers=3):
        self.storage = BaseStorage
        if DOMAIN is None:
            DOMAIN = self.storage.get_unindexed_domain()
        self.storage.insert_domain(DOMAIN)
        self.workers = workers + 1 # Because indexing starting from 0
        self.DEPTH = 0
        self.MAX_DEPTH = max_depth
        self._start_index(DOMAIN)
        self._start_workers()
    
 
    def _start_index(self, DOMAIN):
        self.DOMAIN = DOMAIN
        url = indexerutils.domain_to_url(self.DOMAIN)
        if self.storage.pages_col.find({"url": url, "indexed": True}).count() > 0:
            url = self.storage.get_unindexed_page(self.DOMAIN, self.MAX_DEPTH)
        self._visit_page(url)
        

    def _worker(self):
        while True:
            url = self.storage.get_unindexed_page(self.DOMAIN, self.MAX_DEPTH)
            if not url:
                logger.info(f"worker finished his job")
                break
            if url['depth'] > self.DEPTH:
                logger.info(f"moving into depth {url['depth']}")
                self.DEPTH = url['depth']
                sleep(4)
            if url:
                self._visit_page(url['url'])

    def _start_workers(self):
        workers = []
        logger.info(f"Bootstraping {self.workers} workes.")
        for i in range(self.workers - 1):
            workers.append(Thread(target=self._worker))
        for counter, worker in enumerate(workers):
            logger.info(f"Starting worker {counter + 1}")
            sleep(0.1)
            worker.start()

        for worker in workers: # Wait for all threads to finish
            worker.join() 

        logger.info(f"Scan finished at depth {self.DEPTH}")

    def _visit_page(self, url):
        logger.info(f"visiting page {url}")
        try:
            html = self.request(url)    
            if html:
                internal_links = indexerutils.extract_internal_links(self.DOMAIN, html, url)
                for link in internal_links:
                    #logger.debug(f"iter link: {link}")
                    self.storage.insert_page(link, self.DOMAIN, self.DEPTH + 1)
            self.storage.pages_col.update_one({"url": url}, { "$set": { "indexed": True } })
        except Exception as e:
            logger.debug(e)
            self.storage.pages_col.update_one({"url": url}, { "$set": { "indexed": True } })


