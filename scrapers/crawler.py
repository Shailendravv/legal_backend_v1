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
        # Use args to hide playwright automation markers
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        logger.info("Playwright browser started.")

    async def get_page_html(self, url: str) -> str:
        """
        Fetches the HTML of a page using Playwright.
        """
        if not self.browser:
            await self.start()
            
        # Use a real user agent
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            # Optionally add more headers/fingerprints here
        )
        page: Page = await context.new_page()
        try:
            # More generous delay to let bot-check JS run
            await asyncio.sleep(4)
            logger.debug(f"Crawling URL: {url}")
            
            # Use networkidle to ensure JavaScript components load fully
            response = await page.goto(url, timeout=40000, wait_until="networkidle")
            
            if response and response.status >= 400:
                logger.warning(f"Got HTTP {response.status} for {url}")
            
            html = await page.content()
            return html
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return ""
        finally:
            await page.close()
            await context.close()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright browser stopped.")

crawler = Crawler()
