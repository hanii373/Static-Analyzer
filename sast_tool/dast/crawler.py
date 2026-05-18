# sast_tool/dast/crawler.py
import asyncio
import logging
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebForm:
    """Represents an HTML form discovered during crawling."""
    def __init__(self, action: str, method: str, inputs: list):
        self.action = action
        self.method = method.upper()
        self.inputs = inputs  # List of input names/types

    def __repr__(self):
        return f"WebForm(action='{self.action}', method='{self.method}', inputs={self.inputs})"


class DASTCrawler:
    """
    Asynchronous web crawler that maps attack surfaces 
    by extracting internal links and HTML forms.
    """
    def __init__(self, base_url: str, max_depth: int = 3):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.visited_urls = set()
        self.discovered_forms = {}  # URL -> List[WebForm]

    def _is_internal(self, url: str) -> bool:
        """Ensures the crawler stays within the target domain scoping boundary."""
        return urlparse(url).netloc == self.domain

    async def crawl_page(self, session: aiohttp.ClientSession, url: str, current_depth: int):
        """Recursively parses a single page asynchronously up to max_depth."""
        if url in self.visited_urls or current_depth > self.max_depth:
            return

        self.visited_urls.add(url)
        logger.info(f"Crawling surface: {url} (Depth: {current_depth})")

        try:
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    return
                
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    return

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # 1. Extract and map forms (critical input sinks for DAST fuzzing)
                self.extract_forms(url, soup)

                # 2. Extract and follow links recursively
                tasks = []
                for anchor in soup.find_all("a", href=True):
                    href = anchor["href"]
                    full_url = urljoin(url, href)
                    # Normalize URL by removing fragments
                    full_url = urlparse(full_url)._replace(fragment="").geturl()

                    if self._is_internal(full_url) and full_url not in self.visited_urls:
                        tasks.append(self.crawl_page(session, full_url, current_depth + 1))
                
                if tasks:
                    await asyncio.gather(*tasks)

        except Exception as e:
            logger.debug(f"Failed to crawl page {url}: {e}")

    def extract_forms(self, url: str, soup: BeautifulSoup):
        """Parses HTML forms and catalog inputs as fuzzing vectors."""
        forms = soup.find_all("form")
        if not forms:
            return

        page_forms = []
        for form in forms:
            action = form.get("action", "")
            method = form.get("method", "get")
            full_action_url = urljoin(url, action)

            inputs = []
            for input_tag in form.find_all(["input", "textarea", "select"]):
                input_name = input_tag.get("name")
                if input_name:
                    inputs.append({
                        "name": input_name,
                        "type": input_tag.get("type", "text")
                    })

            page_forms.append(WebForm(full_action_url, method, inputs))

        if page_forms:
            self.discovered_forms[url] = page_forms

    async def start(self):
        """Entry point for running the asynchronous crawl sequencing loop."""
        async with aiohttp.ClientSession() as session:
            await self.crawl_page(session, self.base_url, current_depth=1)
        return {
            "visited_pages": list(self.visited_urls),
            "attack_surface_forms": self.discovered_forms
        }