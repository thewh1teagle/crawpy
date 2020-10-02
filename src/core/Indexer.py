from .Storage import BaseStorage
from .requester import Requester
from loguru import logger
from .utils import indexerutils
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread
from queue import Queue

class Indexer(Requester):
    "Indexing a site domain and saving with base-storage"
    def __init__(self, BaseStorage: BaseStorage, DOMAIN=None, max_depth=2, workers=3):
        self.visited_pages = set()
        self.storage = BaseStorage
        self.inserter_queue = Queue()
        self.indexer_queue = Queue()
        if DOMAIN is None:
            DOMAIN = self.storage.get_unindexed_domain()
        self.storage.insert_domain(DOMAIN)
        self.workers = workers + 1 # Because indexing starting from 0
        self.DEPTH = 0
        self.MAX_DEPTH = max_depth
        self._start_index(DOMAIN)
        self._start_inserter_workers()
        sleep(5)
        self._start_indexer_workers()
        

        
    
 
    def _start_index(self, DOMAIN):
        self.DOMAIN = DOMAIN
        url = indexerutils.domain_to_url(self.DOMAIN)
        if self.storage.pages_col.find({"url": url, "indexed": True}).count() > 0:
            url = self.storage.get_unindexed_pages(self.DOMAIN, self.MAX_DEPTH, limit=1)
        self._visit_page(url)
        

    def indexer_worker(self):
        while True:
            if self.indexer_queue.empty():
                pages = self.storage.get_unindexed_pages(self.DOMAIN, self.MAX_DEPTH)
                if not pages:
                    logger.info(f"worker finished his job")
                    break
                self.indexer_queue.put(pages)
            pages = self.indexer_queue.get()
            if pages[0]['depth'] > self.DEPTH:
                logger.info(f"moving into depth {pages[0]['depth']}")
                self.DEPTH = pages[0]['depth']
                sleep(4)
            for page in pages:
                self._visit_page(page['url'])

    def inserter_worker(self):
        while True:
            for _ in range(5):
                if self.inserter_queue.empty():
                    sleep(15)
                else:
                    break
                
            if self.inserter_queue.empty():
                logger.info('inserter queue empty. shutting down worker.')
                break

            page = self.inserter_queue.get()
            logger.info(f"Inserting urls of page {page['url']} [bulk write]")
            pages = []  
            for link in page['urls']:
                
                # logger.info(f'inserting page {link}')
                pages.append({
                    'domain': page['domain'], 'url': link, 'depth': page['depth'], "indexed": False, "Middle_of_scan": False
                })
                # self.storage.insert_page(link, page['domain'], page['depth'])
            self.storage.insert_pages(page['domain'], page['url'], page['urls'], page['depth'])

    def _start_indexer_workers(self):
        workers = []
        logger.info(f"Bootstraping {self.workers} workes.")
        for _ in range(self.workers - 1):
            workers.append(Thread(target=self.indexer_worker))
        for counter, worker in enumerate(workers):
            logger.info(f"Starting worker {counter + 1}")
            sleep(0.1)
            worker.start()

        for worker in workers: # Wait for all threads to finish
            worker.join() 

        logger.info(f"Scan finished at depth {self.DEPTH}")

    def _start_inserter_workers(self):
        Thread(target=self.inserter_worker).start() 

    def _visit_page(self, url):
        logger.info(f'vising page {url}')
        if url in self.visited_pages:
            return
        else:
            self.visited_pages.add(url)
        logger.info(f"visiting page {url}")
        try:
            html = self.request(url)    
            if html:
                internal_links = indexerutils.extract_internal_links(self.DOMAIN, html, url)
                self.inserter_queue.put({
                    'domain': self.DOMAIN,
                    'url': url,
                    'depth': self.DEPTH + 1,
                    'urls': internal_links
                })
        except Exception as e:
            logger.debug(e)
            self.storage.pages_col.update_one({"url": url}, { "$set": { "indexed": True } })


