import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

def crawl_sources(start_url, max_pages=5):
    """Extract legit script/CSS sources from target site"""
    visited = set()
    sources = {'script': set(), 'style': set()}
    
    try:
        resp = requests.get(start_url, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Extract scripts
        for script in soup.find_all('script', src=True):
            src = urljoin(start_url, script['src'])
            if is_safe_source(src):
                sources['script'].add(src)
        
        # Extract CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = urljoin(start_url, link.get('href'))
            if is_safe_source(href):
                sources['style'].add(href)
                
    except Exception as e:
        print(f"Crawl error: {e}")
    
    return sources

def is_safe_source(url):
    """Filter dangerous sources"""
    bad = ['data:', 'blob:', 'javascript:']
    return not any(b in url.lower() for b in bad)
