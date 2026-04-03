import asyncio
from scrapers.crawler import crawler
from app.core.logger import logger

async def test_scraping():
    print("Testing Playwright Crawler...")
    url = "https://www.wikipedia.org"
    
    try:
        # Start the crawler (launches browser)
        await crawler.start()
        
        # Fetch HTML
        print(f"Fetching content from: {url}")
        html = await crawler.get_page_html(url)
        
        if html:
            logger.info("Successfully scraped HTML!")
            logger.info(f"HTML Length: {len(html)} characters")
            logger.info("Snippet of HTML:")
            logger.info(html[:200])
        else:
            logger.warning("Failed to scrape. HTML returned empty.")
            
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        # Important: Stop the crawler to close the browser
        await crawler.stop()

if __name__ == "__main__":
    asyncio.run(test_scraping())
