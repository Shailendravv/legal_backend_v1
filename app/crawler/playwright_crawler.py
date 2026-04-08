import asyncio
import sys
import hashlib
import random
import time
from pathlib import Path
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from fake_useragent import UserAgent
from app.crawler.base import BaseCrawler
from app.core.logger import logger
from typing import Any

class PlaywrightCrawler(BaseCrawler):
    def _sync_crawl(self, url: str) -> str:
        """Synchronous version of the crawler for Windows compatibility."""
        # High-trust fixed Chrome/Windows UA to match Client Hints
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        with sync_playwright() as p:
            # Use real chrome if available for better fingerprinting
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1366, "height": 768},
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Sec-CH-UA": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    "Sec-CH-UA-Mobile": "?0",
                    "Sec-CH-UA-Platform": '"Windows"',
                    "Referer": "https://www.google.com/"
                }
            )
            page = context.new_page()
            
            # Apply stealth
            Stealth().apply_stealth_sync(page)
            
            # --- Human Interaction Simulation ---
            # 1. Warm up with Google to get some standard cookies
            try:
                page.goto("https://www.google.com", wait_until="networkidle", timeout=10000)
                time.sleep(random.uniform(1, 2))
            except:
                pass
            
            logger.info(f"Using Super-Stealth Sync Crawler for: {url}")
            page.goto(url, wait_until="networkidle", timeout=45000)
            
            # 2. Simulate human presence
            page.mouse.move(random.randint(0, 500), random.randint(0, 500))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(random.uniform(2, 4))
            
            content = page.content()
            browser.close()
            return content

    def __init__(self):
        super().__init__()
        self.cache_dir = Path(".crawler_cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"

    def _is_blocked(self, content: str) -> bool:
        """Check if the content looks like a bot detection / access denied page."""
        block_signals = [
            "Access Denied",
            "bot detection",
            "Please verify you are a human",
            "captcha",
            "unusual traffic",
            "Reference #"  # Akamai reference format
        ]
        return any(signal.lower() in content.lower() for signal in block_signals)

    async def crawl(self, url: str) -> str:
        """Step 1: Playwright Crawler - Fetch raw content from a URL with Caching."""
        logger.info(f"[START] Step 1: Playwright Crawler - Fetching: {url}")
        
        # --- Cache Check ---
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            logger.info(f"🚀 [CACHE HIT] Returning cached content for: {url}")
            return cache_path.read_text(encoding="utf-8")

        logger.info(f"🌐 [NETWORK FETCH] Fetching fresh content for: {url}")
        
        # On Windows, using async_playwright with SelectorEventLoop (Uvicorn's default) 
        # causes NotImplementedError. We use synchronous playwright in a thread as a robust fix.
        use_sync_fallback = False
        if sys.platform == 'win32':
            try:
                loop = asyncio.get_running_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    use_sync_fallback = True
            except Exception as e:
                logger.warning(f"Metadata loop check failed: {e}")
                # Err on the side of caution for Windows
                use_sync_fallback = True

        if use_sync_fallback:
            logger.info("Using sync_playwright fallback for Windows SelectorEventLoop compatibility.")
            try:
                content = await asyncio.to_thread(self._sync_crawl, url)
                
                # --- Guarded Cache Save ---
                if not self._is_blocked(content):
                    cache_path.write_text(content, encoding="utf-8")
                else:
                    logger.warning(f"⚠️ [BLOCK DETECTED] Fetch for {url} looks blocked. Skipping cache.")
                
                return content
            except Exception as e:
                logger.error(f"[ERROR] Sync fallback failed: {str(e)}")
                raise e

        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={"width": 1366, "height": 768},
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Sec-CH-UA": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                        "Sec-CH-UA-Mobile": "?0",
                        "Sec-CH-UA-Platform": '"Windows"',
                        "Referer": "https://www.google.com/"
                    }
                )
                page = await context.new_page()
                
                # Apply stealth
                await Stealth().apply_stealth_async(page)
                
                # 1. Warm up
                try:
                    await page.goto("https://www.google.com", wait_until="networkidle", timeout=10000)
                    await asyncio.sleep(random.uniform(1, 2))
                except:
                    pass
                
                logger.info(f"Using Super-Stealth Async Crawler for: {url}")
                await page.goto(url, wait_until="networkidle", timeout=45000)
                
                # 2. Simulate human presence
                await page.mouse.move(random.randint(0, 500), random.randint(0, 500))
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await asyncio.sleep(random.uniform(2, 4))
                
                # Extract the full HTML content
                content = await page.content()
                
                # Navigate to the target legal source
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Extract the full HTML content
                content = await page.content()
                
                # --- Guarded Cache Save ---
                if not self._is_blocked(content):
                    cache_path.write_text(content, encoding="utf-8")
                else:
                    logger.warning(f"⚠️ [BLOCK DETECTED] Fetch for {url} looks blocked. Skipping cache.")
                
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
