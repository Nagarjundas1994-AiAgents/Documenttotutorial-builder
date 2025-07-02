from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
import uuid

class VectorStoreManager:
    def __init__(self, collection_name="documentation_store"):
        self.collection_name = collection_name
        # Using in-memory for simplicity, change to host='qdrant' if running in docker network
        self.client = QdrantClient(host="localhost", port=6333) 
        self.embeddings = OllamaEmbeddings(model="snowflake-arctic-embed2:568m")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.setup_collection()

    def setup_collection(self):
        try:
            self.client.get_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception:
            print(f"Creating collection '{self.collection_name}'.")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # snowflake-arctic-embed2:568m is 1024-dim
                    distance=models.Distance.COSINE
                )
            )

    def upsert_documents(self, pages_content):
        documents = []
        for page in pages_content:
            chunks = self.text_splitter.split_text(page['content'])
            for chunk in chunks:
                documents.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk,
                    "metadata": {"source_url": page['url']}
                })
        
        if not documents:
            return 0

        texts_to_embed = [doc['text'] for doc in documents]
        vectors = self.embeddings.embed_documents(texts_to_embed)

        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=[doc['id'] for doc in documents],
                vectors=vectors,
                payloads=[{"text": doc['text'], "metadata": doc['metadata']} for doc in documents]
            ),
            wait=True
        )
        return len(documents)

    async def query(self, query_text, limit=5):
        query_vector = self.embeddings.embed_query(query_text)
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [hit.payload for hit in hits]