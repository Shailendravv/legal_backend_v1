import asyncio
from typing import List, Dict
from scrapers.crawler import crawler
from scrapers.html_parser import parse_devgan_ipc_index, parse_devgan_section_page
from app.core.logger import logger

class DevganScraper:
    INDEX_URL = "https://www.devgan.in/ipc/index.php"

    async def scrape_sections(self, limit: int = 10) -> List[Dict]:
        """
        Scrapes multiple IPC sections from devgan.in sequentially.
        """
        logger.info(f"Starting real scrape from {self.INDEX_URL}")
        sections = []
        
        # 1. Fetch index page
        index_html = await crawler.get_page_html(self.INDEX_URL)
        if not index_html:
            logger.error(f"Failed to fetch {self.INDEX_URL}")
            return []
        
        # Log this at INFO level so the user can see it
        logger.info(f"Page fetched. Type: {self.INDEX_URL}, Size: {len(index_html)} bytes.")
        
        if "Access Denied" in index_html or len(index_html) < 2000:
            logger.error("Page content too short or Access Denied. Bot-block detected.")
            return []

        # 2. Parse links
        section_links = parse_devgan_ipc_index(index_html)
        logger.info(f"Found {len(section_links)} section links.")

        # 3. Scrape individual sections (with limit for now)
        count = 0
        for link in section_links:
            if count >= limit:
                break
            
            # More generous delay for bot-checks
            await asyncio.sleep(5)
            section_html = await crawler.get_page_html(link)
            if section_html:
                logger.info(f"Fetched {link}, Size: {len(section_html)} bytes.")
                section_data = parse_devgan_section_page(section_html, link)
                if section_data:
                    sections.append(section_data)
                    count += 1
                    logger.debug(f"Scraped section {section_data['section']} from {link}")
                else:
                    logger.warning(f"Failed to parse section data from {link}")
            else:
                logger.warning(f"Failed to fetch section page: {link}")
        
        logger.info(f"Scraped {len(sections)} sections successfully.")
        return sections

devgan_scraper = DevganScraper()

