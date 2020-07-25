import pymongo
from loguru import logger
import numpy as np
from time import sleep


class BaseStorage:
    "Manage the DB using mongodb as database"
    def __init__(
                self, 
                DB_HOST="localhost", 
                DB_PORT=27017, 
                USER=None, 
                PASSWORD=None, 
                DB_NAME="crawler"
            ):

        self.setup(
                DB_HOST, DB_PORT, DB_NAME, USER, PASSWORD
            )

    def setup(
                self, 
                DB_HOST, 
                DB_PORT, 
                DB_NAME, 
                USER, 
                PASSWORD
            ):

        self._create_connection(DB_HOST, DB_PORT, USER, PASSWORD)
        self._create_db(DB_NAME)
        self._create_collections()

    def _create_db(self, DB_NAME):
        dblist = self.mongo_client.list_database_names()
        if DB_NAME in dblist:
            logger.debug("The database exists.")
        else:
            logger.debug("Created database {}".format(DB_NAME))        
        self.DB = self.mongo_client[DB_NAME]

    def _create_collections(self, domain_col_name="domains", pages_col_name="pages"):
        collist = self.DB.list_collection_names()

        for col in (domain_col_name, pages_col_name):        
            if col in collist:
                logger.debug("The collection {} exists.".format(col))
            else:
                logger.debug("Created {} collection.".format(col))
        self.domain_col = self.DB[domain_col_name]
        self.pages_col = self.DB[pages_col_name]


    def _create_connection(self, DB_HOST, DB_PORT, USER, PASSWORD):
        logger.debug("Connecting to mongodb://{}:{}/".format(DB_HOST, DB_PORT))
        self.mongo_client = pymongo.MongoClient("mongodb://{}:{}/".format(DB_HOST, DB_PORT))
        if self.mongo_client.connect:
            logger.debug("Connected successfuly to database!")

    

    def insert_domain(
                    self,
                    domain,
                    is_sub_domain=False,
                    pages=[],
                    sub_domains=[],
                    in_scan=False,
                    last_scan="None",
                    col_name="domains"
                ):

        self.domain_col.insert({
            "domain": domain,
            "isSubDomain": is_sub_domain,
            "subDomains": sub_domains,
            "in_progress": in_scan,
            "last_scan": last_scan
        })

    
    def valid_page(self, url):
        invalid_extensions = [
            "img",
            "stl",
            "jpg",
            "mp4",
            "mp3",
            "jpeg"
        ]

        return all([
                not url.endswith(extension) for extension in invalid_extensions
            ])


    def insert_page(self, url, domain, depth, scraped=False, urls=None):
        if self.pages_col.find({"url": url}).count() <= 0 and self.valid_page(url):
            logger.debug(f"inserting page {url}")
            self.pages_col.insert({
                "url": url,
                "domain": domain,
                "depth": depth,
                "scraped": False,
                "indexed": False,
                "urls": urls
            })
            
        else:
            logger.debug(f"page {url} exist")
            

    def get_unindexed_page(self, domain, max_depth):
        query = {"domain": domain, "indexed": False, "depth": {'$lte': max_depth}}        
        result = self.pages_col.find_one(query)
        logger.debug(result)
        if not result:
            sleep(2)
        return result

    def get_unindexed_domain(self):
        query = {"indexed": False}
        result = self.domain_col.find(query).limit(1)
        if result:
            logger.debug(result)
        else:
            logger.debug("Not found any unindexed domain in DB.")
            sleep(2)
        return result