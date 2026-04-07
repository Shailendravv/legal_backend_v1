import asyncio
import sys
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from app.crawler.base import BaseCrawler
from app.core.logger import logger
from typing import Any

class PlaywrightCrawler(BaseCrawler):
    def _sync_crawl(self, url: str) -> str:
        """Synchronous version of the crawler for Windows compatibility."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            content = page.content()
            browser.close()
            return content

    async def crawl(self, url: str) -> str:
        """Step 1: Playwright Crawler - Fetch raw content from a URL."""
        logger.info(f"[START] Step 1: Playwright Crawler - Fetching: {url}")
        
        # On Windows, using async_playwright with SelectorEventLoop (Uvicorn's default) 
        # causes NotImplementedError. We use synchronous playwright in a thread as a robust fix.
        if sys.platform == 'win32':
            try:
                loop = asyncio.get_running_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    logger.info("Using sync_playwright fallback for Windows SelectorEventLoop compatibility.")
                    return await asyncio.to_thread(self._sync_crawl, url)
            except Exception as e:
                logger.warning(f"Error checking loop type: {e}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to the target legal source
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Extract the full HTML content
                content = await page.content()
                
                await browser.close()
                logger.info(f"[END] Step 1: Playwright Crawler - Successfully fetched {len(content)} characters.")
                return content
        
        except Exception as e:
            logger.error(f"[ERROR] Step 1: Playwright Crawler failed for {url}: {str(e)}")
            raise e

    def parse(self, raw_html: str) -> Any:
        """Step 2: Placeholder for BeautifulSoup Parsing (to be implemented next)."""
        logger.info("[START] Step 2 Placeholder: Content Parsing (to be implemented)")
        # This will be refined as we move to Step 2
        return {"raw_html_length": len(raw_html)}
