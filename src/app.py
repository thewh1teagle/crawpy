from Storage import BaseStorage
from Indexer import Indexer

def main():
    MAX_DEPTH = 2
    DOMAIN = "kan.org.il"
    storage = BaseStorage()
    indexer = Indexer(storage, DOMAIN)
    


if __name__ == '__main__':
    main()
