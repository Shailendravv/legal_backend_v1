import asyncio
import sys
import hashlib
import random
import time
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Any
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from fake_useragent import UserAgent
from app.crawler.base import BaseCrawler
from app.core.logger import logger

# ---------------------------------------------------------------------------
# LEGAL QUERY PARSING (Ported from Test.py)
# ---------------------------------------------------------------------------

ACT_ALIASES = {
    "ipc": {"name": "Indian Penal Code", "year": "1860", "short": "IPC"},
    "crpc": {"name": "Code of Criminal Procedure", "year": "1973", "short": "CrPC"},
    "cpc": {"name": "Code of Civil Procedure", "year": "1908", "short": "CPC"},
    "it act": {"name": "Information Technology Act", "year": "2000", "short": "IT Act"},
    "constitution": {"name": "Constitution of India", "year": "1950", "short": "Constitution"},
    "motor vehicles act": {"name": "Motor Vehicles Act", "year": "1988", "short": "MV Act"},
    "ndps": {"name": "Narcotic Drugs and Psychotropic Substances Act", "year": "1985", "short": "NDPS"},
    "pocso": {"name": "Protection of Children from Sexual Offences Act", "year": "2012", "short": "POCSO"},
    "bnss": {"name": "Bharatiya Nagarik Suraksha Sanhita", "year": "2023", "short": "BNSS"},
    "bns": {"name": "Bharatiya Nyaya Sanhita", "year": "2023", "short": "BNS"},
    "bsa": {"name": "Bharatiya Sakshya Adhiniyam", "year": "2023", "short": "BSA"},
}

@dataclass
class ParsedQuery:
    raw: str
    act_alias: str          # e.g. "ipc"
    act_name: str           # e.g. "Indian Penal Code"
    act_year: str           # e.g. "1860"
    section: Optional[str]  # e.g. "420"
    search_term: str        # fallback search string

def parse_legal_query(query: str) -> ParsedQuery:
    """Parse a query like 'IPC 420', 'Section 302 of IPC', etc."""
    query_lower = query.lower().strip()
    section_match = re.search(r'\b(\d+[A-Za-z]?)\b', query)
    section = section_match.group(1) if section_match else None

    matched_alias = None
    matched_meta = None
    for alias, meta in ACT_ALIASES.items():
        if alias in query_lower:
            matched_alias = alias
            matched_meta = meta
            break

    if matched_meta:
        search_term = matched_meta['name']
        if section:
            search_term = f"Section {section} {matched_meta['name']}"
        
        return ParsedQuery(
            raw=query,
            act_alias=matched_alias,
            act_name=matched_meta["name"],
            act_year=matched_meta["year"],
            section=section,
            search_term=search_term,
        )

    return ParsedQuery(
        raw=query,
        act_alias="unknown",
        act_name="Unknown Act",
        act_year="",
        section=section,
        search_term=query,
    )

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
        
    async def dynamic_crawl(self, user_query: str) -> dict:
        """
        Dynamically search and crawl legal content based on user query.
        Falls back to synchronous execution on Windows if ProactorEventLoop is not available.
        """
        # --- Windows Event Loop Fix ---
        use_sync_fallback = False
        if sys.platform == 'win32':
            try:
                loop = asyncio.get_running_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    use_sync_fallback = True
            except Exception:
                use_sync_fallback = True

        if use_sync_fallback:
            logger.info("Using sync_playwright fallback for dynamic_crawl (Windows compatibility)")
            return await asyncio.to_thread(self._sync_dynamic_crawl, user_query)

        parsed = parse_legal_query(user_query)
        logger.info(f"🚀 [DYNAMIC CRAWL] Query: {user_query} | Resolved: {parsed.act_name}")

        base_url = "https://www.indiacode.nic.in"
        result_text = None
        strategy_used = "none"

        async with async_playwright() as p:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": random.randint(1280, 1440), "height": random.randint(720, 900)},
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
            await Stealth().apply_stealth_async(page)

            # --- Human Interaction Warm-up ---
            try:
                await page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(random.uniform(1.5, 2.5))
                await page.mouse.move(random.randint(100, 400), random.randint(100, 400))
            except: pass

            # Strategy 1: Direct URL
            KNOWN_HANDLES = {
                "ipc": "123456789/2263", "crpc": "123456789/1353", "cpc": "123456789/1358",
                "bns": "123456789/17121", "bnss": "123456789/17122", "bsa": "123456789/17123",
            }
            handle = KNOWN_HANDLES.get(parsed.act_alias)
            if handle and parsed.section:
                direct_url = f"{base_url}/handle/{handle}?view=1&index=1"
                try:
                    await page.goto(direct_url, wait_until="domcontentloaded", timeout=20000)
                    result_text = await self._extract_section_from_page(page, parsed.section)
                    if result_text and len(result_text.strip()) > 100: strategy_used = "direct_url"
                except PlaywrightTimeout: pass

            # Strategy 2: Site Search
            if not result_text or len(result_text.strip()) < 100:
                search_url = f"{base_url}/search?query={parsed.search_term.replace(' ', '+')}&searchType=section"
                try:
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
                    await page.wait_for_timeout(2000)
                    results = await page.query_selector_all("a.search-result-link, .result-title a, table a")
                    for result in results[:5]:
                        href = await result.get_attribute("href")
                        text = await result.inner_text()
                        if href and parsed.section and parsed.section in text:
                            full_url = href if href.startswith("http") else base_url + href
                            await page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
                            result_text = await self._extract_page_text(page)
                            if result_text and len(result_text.strip()) > 100:
                                strategy_used = "site_search"
                                break
                    if not result_text:
                        result_text = await self._extract_page_text(page)
                        strategy_used = "site_search_fallback"
                except PlaywrightTimeout: pass

            await browser.close()

        # Final Fallback
        if not result_text or len(result_text.strip()) < 100:
            result_text = f"⚠️ Section {parsed.section} of {parsed.act_name} not found on indiacode.nic.in."
            strategy_used = "fallback_guidance"

        return {"query": user_query, "parsed_act": parsed.act_name, "parsed_section": parsed.section, "content": result_text, "strategy": strategy_used}

    def _sync_dynamic_crawl(self, user_query: str) -> dict:
        """Synchronous version of dynamic_crawl for Windows compatibility."""
        parsed = parse_legal_query(user_query)
        base_url = "https://www.indiacode.nic.in"
        result_text, strategy_used = None, "none"

        with sync_playwright() as p:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
            context = browser.new_context(
                user_agent=user_agent, 
                viewport={"width": random.randint(1280, 1440), "height": random.randint(720, 900)},
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
            Stealth().apply_stealth_sync(page)

            # --- Human Interaction Warm-up ---
            try:
                page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=10000)
                time.sleep(random.uniform(1.5, 2.5))
                page.mouse.move(random.randint(100, 400), random.randint(100, 400))
            except: pass

            # Strategy 1: Direct URL
            KNOWN_HANDLES = { "ipc": "123456789/2263", "crpc": "123456789/1353", "cpc": "123456789/1358", "bns": "123456789/17121", "bnss": "123456789/17122", "bsa": "123456789/17123" }
            handle = KNOWN_HANDLES.get(parsed.act_alias)
            if handle and parsed.section:
                try:
                    page.goto(f"{base_url}/handle/{handle}?view=1&index=1", wait_until="domcontentloaded", timeout=20000)
                    result_text = self._sync_extract_section(page, parsed.section)
                    if result_text and len(result_text.strip()) > 100: strategy_used = "direct_url"
                except: pass

            # Strategy 2: Site Search
            if not result_text or len(result_text.strip()) < 100:
                try:
                    search_url = f"{base_url}/search?query={parsed.search_term.replace(' ', '+')}&searchType=section"
                    page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
                    time.sleep(2)
                    results = page.query_selector_all("a.search-result-link, .result-title a, table a")
                    for result in results[:5]:
                        href, text = result.get_attribute("href"), result.inner_text()
                        if href and parsed.section and parsed.section in text:
                            page.goto(href if href.startswith("http") else base_url + href, wait_until="domcontentloaded", timeout=20000)
                            result_text = self._sync_extract_text(page)
                            if result_text and len(result_text.strip()) > 100:
                                strategy_used = "site_search"
                                break
                except: pass

            # Strategy 3: Homepage Search Navigation (Most Human-like)
            if not result_text or len(result_text.strip()) < 100:
                try:
                    page.goto(base_url, wait_until="domcontentloaded", timeout=20000)
                    time.sleep(random.uniform(2, 3))
                    search_box = page.query_selector('input[name="query"]') or page.query_selector('input[type="search"]') or page.query_selector('#searchInput')
                    if search_box:
                        search_box.fill(parsed.search_term)
                        time.sleep(random.uniform(0.5, 1.5))
                        search_box.press("Enter")
                        page.wait_for_load_state("networkidle", timeout=20000)
                        result_text = self._sync_extract_text(page)
                        
                        # If no results with specific term, try just the section and act name separately or broader
                        if not result_text or "no results" in result_text.lower():
                            logger.info("Specific search failed, trying broader Act search")
                            search_box.fill(parsed.act_name)
                            search_box.press("Enter")
                            page.wait_for_load_state("networkidle", timeout=20000)
                            result_text = self._sync_extract_text(page)

                        if result_text and len(result_text.strip()) > 100: strategy_used = "homepage_nav"
                except: pass

            browser.close()

        if not result_text or len(result_text.strip()) < 100:
            result_text = f"⚠️ Section {parsed.section} of {parsed.act_name} not found."
            strategy_used = "fallback_guidance"

        return {"query": user_query, "parsed_act": parsed.act_name, "parsed_section": parsed.section, "content": result_text, "strategy": strategy_used}

    def _sync_extract_section(self, page: Any, section: str) -> Optional[str]:
        selectors = [f'text=Section {section}', f'h2:has-text("{section}")']
        for sel in selectors:
            el = page.query_selector(sel)
            if el:
                parent = el.evaluate_handle("el => el.closest('.section, article, .content, div')")
                if parent:
                    text = page.evaluate("el => el.innerText", parent)
                    if text and len(text.strip()) > 50: return text.strip()
        return self._sync_extract_text(page)

    def _sync_extract_text(self, page: Any) -> str:
        """Sync version of text extraction with error detection."""
        try:
            # Detect DSpace Error pages or Akamai Blocks or Empty Results
            content = page.content()
            block_signals = ["Invalid URL or Argument", "experienced an error", "Access Denied", "Reference #", "bot detection", "Search produced no results"]
            if any(signal in content for signal in block_signals):
                logger.warning(f"Detected Block/Error/Empty page (sync): {content[:100]}...")
                return ""

            for sel in ['.section-content', '#content', 'main', 'article']:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text()
                    if text and len(text.strip()) > 100: return text.strip()
            return page.evaluate("() => document.body.innerText.trim()")
        except: return ""

    async def _extract_section_from_page(self, page: Page, section: str) -> Optional[str]:
        """Try to find and return text for a specific section on the current page."""
        selectors = [f'text=Section {section}', f'h2:has-text("{section}")', f'.section-title:has-text("{section}")']
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    parent = await el.evaluate_handle("el => el.closest('.section, article, .content, div')")
                    if parent:
                        text = await page.evaluate("el => el.innerText", parent)
                        if text and len(text.strip()) > 50:
                            return text.strip()
            except Exception: continue
        return await self._extract_page_text(page)

    async def _extract_page_text(self, page: Page) -> str:
        """Extract meaningful text from current page, filtering noise and detecting errors."""
        try:
            # Detect DSpace Error pages or Akamai Blocks or Empty Results
            content = await page.content()
            block_signals = ["Invalid URL or Argument", "experienced an error", "Access Denied", "Reference #", "bot detection", "Search produced no results"]
            if any(signal in content for signal in block_signals):
                logger.warning(f"Detected Block/Error/Empty page: {content[:100]}...")
                return ""

            for sel in ['.section-content', '#content', 'main', 'article']:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if text and len(text.strip()) > 100: return text.strip()
            return await page.evaluate("""() => {
                const remove = ['nav', 'header', 'footer', 'script', 'style'];
                remove.forEach(sel => document.querySelectorAll(sel).forEach(el => el.remove()));
                return document.body.innerText.trim();
            }""")
        except Exception as e: return f"Extraction error: {e}"

    def parse(self, raw_html: str) -> Any:
        """Step 2: Placeholder for BeautifulSoup Parsing (to be implemented next)."""
        logger.info("[START] Step 2 Placeholder: Content Parsing (to be implemented)")
        # This will be refined as we move to Step 2
        return {"raw_html_length": len(raw_html)}
