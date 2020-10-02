import pymongo
import numpy as np
from loguru import logger
from time import sleep
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import InsertOne, UpdateOne
import sys

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
            logger.info("The database exists.")
        else:
            logger.info("Created database {}".format(DB_NAME))        
        self.DB = self.mongo_client[DB_NAME]

    def _create_collections(self, domain_col_name="domains", pages_col_name="pages"):
        collist = self.DB.list_collection_names()

        for col in (domain_col_name, pages_col_name):        
            if col in collist:
                logger.info("The collection {} exists.".format(col))
            else:
                logger.info("Created {} collection.".format(col))
        self.domain_col = self.DB[domain_col_name]
        self.pages_col = self.DB[pages_col_name]


    def _create_connection(self, DB_HOST, DB_PORT, USER, PASSWORD):
        logger.info("Connecting to mongodb://{}:{}/".format(DB_HOST, DB_PORT))
        self.mongo_client = pymongo.MongoClient("mongodb://{}:{}/".format(DB_HOST, DB_PORT), serverSelectionTimeoutMS=5000)
        try:
            info = self.mongo_client.server_info() # Forces a call.
        except ServerSelectionTimeoutError:
            logger.error("Mongodb server is down.")
            sys.exit(1)
        logger.info("Connected successfuly to mongodb.")


    

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
        invalid_extensions = (
            "img",
            "stl",
            "jpg",
            "mp4",
            "mp3",
            "jpeg"
        )

        return not any(
            url.endswith(extension) for extension in invalid_extensions
        )

    def set_indexed(self, url, indexed=True):
        self.pages_col.update_one({'url': url}, {"$set": {'indexed': indexed}})

    def insert_pages(self, domain, parent, urls, depth):
        pages = []
        for url in urls:
            pages.append(
                {"domain": domain, "url": url, "depth": depth, "middleScan": False, "indexed": False}
            )
        pages_objects = []
        for page in pages:
            pages_objects.append(
                UpdateOne(
                    {'url': page['url']}, {"$setOnInsert": page}, upsert=True
                )
            )
        result = self.pages_col.bulk_write(pages_objects)
        self.set_indexed(parent)
        return result

    def get_unindexed_pages(self, domain, max_depth, limit=10):
        query = {"domain": domain, "indexed": False, 'middleScan': False, "depth": {'$lte': max_depth}}
        result = self.pages_col.find(query, limit=limit)
        result = list(result)
        if not result:
            print("No result")
        else:
            urls = [page['url'] for page in result]
            self.set_middle_scan(urls, middle=True)
            return result

    def set_middle_scan(self, urls, middle=True):
        updates = []
        for url in urls:
            updates.append(
                UpdateOne({
                    'url': url
                    },
                    {"$set": {'middleScan': middle}}
                )
            )
        result = self.pages_col.bulk_write(updates)
        return result


    def get_unindexed_domain(self):
        query = {"indexed": False}
        result = self.domain_col.find(query).limit(1)
        if result:
            logger.info(result)
        else:
            logger.debug("Not found any unindexed domain in DB.")
            sleep(2)
        return result