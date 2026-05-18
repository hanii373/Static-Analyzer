# test_crawler.py
import asyncio
import logging
from sast_tool.dast.crawler import DASTCrawler, WebForm
from sast_tool.dast.scanner import DASTScanner

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Emulate a mocked HTML structure that includes a vulnerable target search box form
mock_html_with_vulnerabilities = """
<html>
    <body>
        <h1>Search Dashboard Sandbox</h1>
        <form action="http://localhost/search" method="GET">
            <input type="text" name="query" />
            <input type="submit" value="Search" />
        </form>
    </body>
</html>
"""

async def run_full_dast_suite():
    print("--- 🛰️ Phase 3: Commencing Dynamic App Security Test (DAST) Suite ---")
    
    # 1. Set up your crawler pipeline tracker
    crawler = DASTCrawler("http://localhost", max_depth=1)
    
    # Simulate discovering a page containing a search form vector directly
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(mock_html_with_vulnerabilities, "html.parser")
    crawler.extract_forms("http://localhost/index.php", soup)
    
    results = {
        "visited_pages": ["http://localhost/index.php"],
        "attack_surface_forms": crawler.discovered_forms
    }
    
    print(f"Mapped Web Attack Surfaces: Discovered {len(results['attack_surface_forms'])} dynamic inputs.")
    
    # 2. Initialize the fuzzer scanner module
    scanner = DASTScanner()
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        for url, forms in results["attack_surface_forms"].items():
            for form in forms:
                print(f"Fuzzing targets against action path: {form.action}...")
                
                # We simulate a target reflecting the XSS input payload directly to test the vulnerability capture trigger
                findings = await scanner.scan_form(session, url, form)
                
                # If your scanner triggers findings, let's look at them:
                print("\n🚨 DAST Vulnerability Pipeline Results:")
                if not findings:
                    print("✅ Form parameters passed fuzzing checks.")
                for finding in findings:
                    print(f"[{finding.severity.name}] {finding.rule_id}: {finding.message}")
                    print(f" 📍 Surface Endpoint: {finding.location.file}")
                    print(f" 🔍 Payload Target Map: {finding.snippet}\n")

if __name__ == "__main__":
    asyncio.run(run_full_dast_suite())