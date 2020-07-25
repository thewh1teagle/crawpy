import requests
from loguru import logger

class Requester:
    def request(self, url) -> str:
        try:
            result = requests.get(url)
            if result.status_code != 200:
                logger.debug("{} with status code of {}".format(url, result.status_code))
            else:
                return result.text
        except Exception as e:
            logger.exception(e)