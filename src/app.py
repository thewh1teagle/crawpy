from Storage import BaseStorage
from Indexer import Indexer
from loguru import logger

def main():
    DOMAIN = "kan.org.il"
    storage = BaseStorage()
    indexer = Indexer(storage, DOMAIN, max_depth=2, workers=5)
    
if __name__ == '__main__':
    main()
