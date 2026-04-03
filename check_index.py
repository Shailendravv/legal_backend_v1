import asyncio
from scrapers.crawler import crawler

async def check_index():
    url = "https://www.devgan.in/ipc/index.php"
    await crawler.start()
    html = await crawler.get_page_html(url)
    print(f"HTML Length: {len(html)}")
    print("HTML Snippet (first 1000):")
    print(html[:1000])
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    print(f"Total links: {len(links)}")
    if links:
        print("First 10 links:", links[:10])
    ipc_links = [l for l in links if 'section=' in l or '/ipc/' in l]
    print(f"Potential IPC links: {len(ipc_links)}")
    if ipc_links:
        print("Sample IPC link:", ipc_links[0])
    
    await crawler.stop()

if __name__ == "__main__":
    asyncio.run(check_index())
