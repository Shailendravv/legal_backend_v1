from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from app.core.logger import logger

def parse_devgan_ipc_index(html: str) -> List[str]:
    """
    Extracts all IPC section URLs from the index page.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    # In Devgan.in, the sections are usually in a list or table
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Be more flexible with the link pattern
        if '/ipc/section/' in href or 'section=' in href:
            if not href.startswith('http'):
                # Ensure it has a domain
                href = f"https://www.devgan.in{'' if href.startswith('/') else '/'}{href}"
            links.append(href)
    
    unique_links = sorted(list(set(links))) # Sorted for consistency
    logger.info(f"Extracted {len(unique_links)} unique section links from index.")
    return unique_links

def parse_devgan_section_page(html: str, url: str) -> Optional[Dict]:
    """
    Parses a single IPC section page and returns structured content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find the section title and content
    # The structure on devgan.in is often: <h1>Section Number - Title</h1>
    h1 = soup.find('h1')
    if not h1:
        return None
        
    title_text = h1.get_text().strip()
    # "Section 302 - Punishment for murder"
    
    # The actual content is usually in the following paragraphs or a specific div
    # Devgan often uses a div with class 'content' or just plain <p> tags after the h1
    content_div = soup.find('div', id='content') or soup.find('div', class_='content')
    if content_div:
        content = content_div.get_text().strip()
    else:
        # Fallback: get all text after h1 until next heading or end
        content = ""
        for sibling in h1.find_next_siblings(['p', 'div']):
            content += sibling.get_text() + "\n"
    
    # Extract section number and title from title_text
    # "Section 302 - Punishment for murder"
    section_num = "Unknown"
    if "Section" in title_text:
        parts = title_text.split('-', 1)
        section_num = parts[0].replace('Section', '').strip()
        title = parts[1].strip() if len(parts) > 1 else title_text
    else:
        title = title_text

    return {
        "id": f"IPC-{section_num}",
        "act": "IPC",
        "section": section_num,
        "title": title,
        "content": content.strip(),
        "source_url": url
    }
