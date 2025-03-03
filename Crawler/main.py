import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import deque
from urllib.robotparser import RobotFileParser

# Initialize settings
USER_AGENT = "ProductCrawlerBot/1.0"  # Identify your crawler
visited = set()
queue = deque(["example1.com", "http://example2.com", "example3.com"])
robots_cache = {}  # Cache parsed robots.txt files per domain


def fetch_page(url):
    """Fetch a page with proper URL normalization and headers."""
    # Ensure URL has a scheme (default to http:// if missing)
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=10
        )
        return response.text if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None


def check_robots_permission(url):
    """
    Check if crawling `url` is allowed by robots.txt rules.
    Returns True if allowed, False otherwise.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Extract domain (e.g., "example.com")

    # Check cache for existing robots.txt rules
    if domain not in robots_cache:
        robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
        rp = RobotFileParser()
        try:
            response = requests.get(
                robots_url,
                headers={"User-Agent": USER_AGENT},
                timeout=5
            )
            if response.status_code == 200:
                rp.parse(response.text.splitlines())
            else:
                rp = None  # Treat missing robots.txt as "allow all"
        except requests.exceptions.RequestException:
            rp = None
        robots_cache[domain] = rp

    # Check if crawling is allowed
    rp = robots_cache[domain]
    if rp and not rp.can_fetch(USER_AGENT, url):
        return False
    return True


def extract_links(html, base_url):
    """Extract and normalize links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        links.append(full_url)
    return links


def is_product_url(url):
    product_patterns = ["/product/", "/p/", "/item/", "product_id="]
    return any(pattern in url for pattern in product_patterns)

# Main crawling loop
while queue:
    url = queue.popleft()

    # Normalize URL and check robots.txt
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    parsed_url = urlparse(url)

    # Skip URLs blocked by robots.txt
    if not check_robots_permission(url):
        print(f"Blocked by robots.txt: {url}")
        continue

    # Process the URL if not visited
    if url not in visited:
        visited.add(url)
        print(f"Crawling: {url}")
        html = fetch_page(url)
        if html:
            links = extract_links(html, url)
            for link in links:
                if is_product_url(link):
                    print(f"Found product: {link}")
                else:
                    if link not in visited:
                        queue.append(link)