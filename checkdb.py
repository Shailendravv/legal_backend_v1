# Create a file called check_db.py
from app.db.vector_store import vector_store
all_docs = vector_store.get_all_documents()
print(f"Total documents in database: {len(all_docs)}")
