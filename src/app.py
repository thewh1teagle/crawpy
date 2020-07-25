from Storage import BaseStorage
from Indexer import Indexer
from loguru import logger

def main():
    MAX_DEPTH = 2
    DOMAIN = "smallwebsite.us"
    storage = BaseStorage()
    indexer = Indexer(storage, DOMAIN, max_depth=MAX_DEPTH)
    
if __name__ == '__main__':
    main()
