from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
import uuid
import time

class VectorStoreManager:
    def __init__(self, collection_name="documentation_store"):
        self.collection_name = collection_name
        self.client = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self._initialize_services()

    def _initialize_services(self):
        """Initialize Qdrant and Ollama services with error handling."""
        # Initialize Qdrant client
        try:
            self.client = QdrantClient(host="localhost", port=6333)
            # Test connection
            self.client.get_collections()
            print("✅ Connected to Qdrant successfully")
            self.setup_collection()
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            print("   Please start Qdrant: docker-compose up -d qdrant")
            self.client = None

        # Initialize Ollama embeddings
        try:
            self.embeddings = OllamaEmbeddings(model="snowflake-arctic-embed2:568m")
            # Test embeddings
            test_embedding = self.embeddings.embed_query("test")
            if test_embedding:
                print("✅ Connected to Ollama successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("   Please ensure Ollama is running and model is available:")
            print("   ollama serve")
            print("   ollama pull snowflake-arctic-embed2:568m")
            self.embeddings = None

    def setup_collection(self):
        if not self.client:
            return
        
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
        if not self.client or not self.embeddings:
            print("⚠️  Vector store or embeddings not available. Skipping document storage.")
            return 0
            
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

        try:
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
        except Exception as e:
            print(f"Error upserting documents: {e}")
            return 0

    async def query(self, query_text, limit=5):
        if not self.client or not self.embeddings:
            print("⚠️  Vector store or embeddings not available. Cannot perform query.")
            return []
            
        try:
            query_vector = self.embeddings.embed_query(query_text)
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [hit.payload for hit in hits]
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return []