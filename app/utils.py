import requests
from bs4 import BeautifulSoup

TIMEOUT = 10

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

def fetch_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes
        return BeautifulSoup(response.text, "lxml")
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching {url}: {e}")
        return None

def text_changed(old_text, new_text):
    return old_text != new_text

