import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class DASTCrawler:
    def __init__(self, target_url):
        self.target_url = target_url
        self.base_domain = urlparse(target_url).netloc
        self.visited = set()
        self.endpoints = []

    async def crawl(self, url=None):
        url = url or self.target_url
        if url in self.visited or urlparse(url).netloc != self.base_domain:
            return # Scope guard: ignore external domains

        self.visited.add(url)
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                
                for link in soup.find_all("a", href=True):
                    full_url = urljoin(url, link["href"])
                    self.endpoints.append(full_url)
                    await self.crawl(full_url)
            except Exception as e:
                print(f"Error crawling {url}: {e}")