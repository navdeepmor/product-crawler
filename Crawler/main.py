import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque

visited = set()
queue = deque(["example1.com", "http://example2.com", "example3.com"])

def fetch_page(url):
    # Add a default scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        links.append(full_url)
    return links

def is_product_url(url):
    product_patterns = ["/product/", "/item/", "product_id="]
    return any(pattern in url for pattern in product_patterns)

while queue:
    url = queue.popleft()
    if url not in visited:
        visited.add(url)
        html = fetch_page(url)
        if html:
            links = extract_links(html, url)
            for link in links:
                if is_product_url(link):
                    print("Found product:", link)
                else:
                    queue.append(link)