import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from loguru import logger


def fix_url(url):
    pass

def domain_to_url(DOMAIN):
    if not "http" in DOMAIN:
        domain_url = "http://" + DOMAIN
    if not DOMAIN.endswith("/"):
        domain_url += "/"
    return domain_url

def extract_domain(url):
    parsed_uri = urlparse(url)
    return parsed_uri.netloc


def extract_links(html):
    extracted_links = []
    soup = BeautifulSoup(html, features='html.parser')
    for link in soup.find_all('a', href=True):
        extracted_links.append(link['href'])
    return extracted_links

def filter_internal_links(domain, links, root_url):
    internal_links = []
    for link in links:
        if domain in link:
            internal_links.append(link)
        elif link.startswith("/"):
            if not link.endswith("/"): link += "/"
            internal_links.append(
                root_url + link[1:]
            )
    logger.info(f"found {len(internal_links)} internal links in {domain}")
    return internal_links

def extract_internal_links(domain, html, root_url):
    links = extract_links(html)
    logger.info(f"found {len(links)} links in {domain}")
    internal_links = filter_internal_links(domain, links, root_url)
    return internal_links
