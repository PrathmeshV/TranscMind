import chromadb
from chromadb.config import Settings
import json
import os

client = chromadb.Client(Settings(chroma_db_impl="chromadb.db.duckdb.DuckDB", persist_directory=os.path.abspath('./api/rag/chroma_db')))

def build_db(taxonomy_path: str = 'api/models/taxonomy.json'):
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    try:
        collection = client.create_collection(name='merchants')
    except Exception:
        collection = client.get_collection('merchants')
    ids = []
    metadatas = []
    documents = []
    for i, item in enumerate(taxonomy.get('examples', [])):
        ids.append(str(i))
        documents.append(item['text'])
        metadatas.append({'category': item['category']})
    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        client.persist()

if __name__ == '__main__':
    os.makedirs(os.path.dirname(os.path.abspath('api/rag/chroma_db')), exist_ok=True)
    build_db()
