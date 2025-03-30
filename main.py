from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
import psycopg2

# Database configuration
DB_CONFIG = {
    "dbname": "vector_db",
    "user": "pgvector_user",
    "password": "SuperSecretTestPassword",
    "host": "localhost",
    "port": "5432"
}

# Initialize Ollama models
def setup_models():
    # Embedding model (bge-m3)
    Settings.embed_model = OllamaEmbedding(
        model_name="bge-m3:latest",
        base_url="http://localhost:11434"
    )
    
    # LLM model (llama3.2)
    Settings.llm = Ollama(
        model="llama3.2:latest",
        base_url="http://localhost:11434",
        request_timeout=300.0
    )

# Initialize pgvector database connection
def init_vector_store():
    try:
        vector_store = PGVectorStore.from_params(
            database=DB_CONFIG["dbname"],
            host=DB_CONFIG["host"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            table_name="document_embeddings",
            embed_dim=1024,  # bge-m3 produces 1024-dimensional embeddings
        )
        return vector_store
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Upload and embed documents
def upload_documents(directory_path):
    # Read documents from directory
    documents = SimpleDirectoryReader(directory_path).load_data()
    
    # Initialize vector store
    vector_store = init_vector_store()
    if not vector_store:
        return False
    
    # Create index with pgvector storage
    index = VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        show_progress=True
    )
    
    print(f"Successfully embedded {len(documents)} documents")
    return index

# Query the database
def query_documents(query_str, index):
    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=3,  # Return top 3 most similar documents
        response_mode="compact"
    )
    
    # Execute query
    response = query_engine.query(query_str)
    return response

def main():
    # Setup models
    setup_models()
    
    # Directory containing your documents
    documents_dir = "./documents"  # Change this to your documents folder
    
    # Upload documents (run this once to embed documents)
    index = upload_documents(documents_dir)
    if not index:
        print("Failed to upload documents")
        return
    
    # Example queries
    while True:
        query = input("\nEnter your query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        try:
            response = query_documents(query, index)
            print("\nResponse:", response.response)
            print("\nSources:")
            for node in response.source_nodes:
                print(f"- {node.node.metadata.get('file_name', 'Unknown')}: "
                      f"Score: {node.score:.3f}")
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    # Create the table if it doesn't exist
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id UUID PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding VECTOR(1024)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")
        exit(1)
    
    main()