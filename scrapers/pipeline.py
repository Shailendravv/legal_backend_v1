from scrapers.sources.devgan import devgan_scraper
from app.db.vector_store import vector_store
from app.utils.embedder import embedder
from app.core.logger import logger
from typing import List, Dict

class IngestionPipeline:
    def __init__(self):
        pass

    async def run_full_pipeline(self):
        """
        Runs the full ingestion process: Scrape -> Embed -> Multi-Save (ChromaDB).
        """
        logger.info("Starting master ingestion pipeline...")
        
        # 1. Scrape
        scraped_sections: List[Dict] = await devgan_scraper.scrape_sections(limit=5) # Limit to 5 for now


        # 2. Process and Upsert
        for item in scraped_sections:
            content = item['content']
            chunk_id = item['id']
            metadata = {
                "act": item['act'],
                "section": item['section'],
                "title": item['title'],
                "source_url": item.get('source_url', '')
            }

            # Embed
            embedding = embedder.embed_document(content)

            # Save to Vector Store
            vector_store.upsert_chunk(
                id=chunk_id,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
        logger.info(f"Ingestion pipeline completed. Processed {len(scraped_sections)} items.")

pipeline = IngestionPipeline()

