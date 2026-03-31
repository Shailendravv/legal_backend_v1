import asyncio
from playwright.async_api import async_playwright, Page, Browser
from typing import List, Dict, Optional, Callable
from app.core.logger import logger

class Crawler:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Playwright browser started.")

    async def get_page_html(self, url: str) -> str:
        """
        Fetches the HTML of a page using Playwright.
        """
        if not self.browser:
            await self.start()
            
        page: Page = await self.browser.new_page()
        try:
            # Respectful delay between requests
            await asyncio.sleep(1)
            logger.debug(f"Crawling URL: {url}")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            html = await page.content()
            return html
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return ""
        finally:
            await page.close()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright browser stopped.")

crawler = Crawler()
