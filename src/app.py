from Storage import BaseStorage
from Indexer import Indexer

def main():
    DOMAIN = "walla.co.il"
    storage = BaseStorage()
    indexer = Indexer(storage, DOMAIN)
    


if __name__ == '__main__':
    main()
