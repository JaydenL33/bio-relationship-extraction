from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, PromptTemplate
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
import psycopg2
import os
import shutil

# Base URL

# This is because I am hosting ollama locally
# on my machine and I want to use the ollama API
# to access the models
# Ollama API base URL
# I had to change oLLama to run on 0.0.0.0 (all interfaces)
# to access it from the host machine
# This is the IP address of my host machine within the WSL environment (found via ifconfig)
# and the port number I used to run ollama

# Setup
custom_prompt = PromptTemplate(
    """This is a system prompt, for you:\n
    We have provided context information below.\n
    ---------------------\n
    {context_str}\n
    ---------------------\n
    Given this information, please answer the question: {query_str}\n
    If the query is asking for information of the same type as in the context (e.g., relationships such as ISOLATED_FROM, METABOLITE_OF, PRODUCES).\n
    Please refrain from using generic terms like "marine organisms" or "bacteria" in your answer.\n
    Instead, use the specific names of the organisms or chemicals mentioned in the context.\n
    Present the answer in the same structured format as shown below:\n
    ---------------------\n
    entity1 RELATION entity2\n
    ---------------------\n
    Then, on a new line, provide a natural language explanation or summary of the result.\n
    There is an example below\n
    Question: \n
    From what organisms is neomycin isolated?\n
    Answer:\n
    ---------------------\n
    neomycin (chemical) ISOLATED_FROM streptomyces rimosus forma paromomycinus (orgamism)\n
    streptomyces rimosus forma paromomycinus (orgamism) PRODUCES neomycin (chemical)\n
    neomycin (chemical) METABOLITE_OF neamine (chemical) \n
    neomycin (chemical) ISOLATED_FROM streptomyces fradiae (organism)\n
    ---------------------\n
    Natural Language Response:
    Neomycin is isolated from two different strains of Streptomyces bacteria: *Streptomyces rimosus forma paromomycinus* and *Streptomyces fradiae*\n
    If a query is asking for information that is not present in the context, please respond with "I don't know" or "Not found".\n""")

base_url = "172.20.80.1:11434"

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
        base_url="http://172.20.80.1:11434"
    )

    # LLM model (llama3.2)
    Settings.llm = Ollama(
        model="deepseek-r1:7b",
        base_url="http://172.20.80.1:11434"
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
            hybrid_search=True
        )
        return vector_store
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Upload and embed documents


def upload_documents(directory_path, processed_dir="./processed_documents"):
    # Create processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)
    
    # Read documents from directory
    documents = SimpleDirectoryReader(directory_path).load_data()
    
    if not documents:
        print("No documents found to embed")
        return False
    
    # Initialize vector store
    vector_store = init_vector_store()
    if not vector_store:
        return False

    try:
        # Create index with pgvector storage - properly configure storage context
        storage_context = vector_store.get_storage_context()
        
        # Create index ensuring that we use the PostgreSQL vector store
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            storage_context=storage_context,
            show_progress=True
        )
        
        # No need to persist as the index is already stored in PostgreSQL
        # index.storage_context.persist() - remove this line
        
        print(f"Successfully embedded {len(documents)} documents")
        
        # Move embedded files to processed directory
        for doc in documents:
            file_path = doc.metadata.get("file_path")
            if file_path and os.path.exists(file_path):
                destination = os.path.join(processed_dir, os.path.basename(file_path))
                print(f"Moving {file_path} to {destination}")
                shutil.move(file_path, destination)
        
        return index
    except Exception as e:
        print(f"Error embedding documents: {e}")
        return False
# Query the database


def query_documents(query_str: str, index: VectorStoreIndex):
    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        qa_prompt=custom_prompt  # Use our custom prompt defined at the top
    )
    
    # Execute query and return response
    response = query_engine.query(query_str)
    return response

def main():
    # Setup models
    setup_models()

    # Directory containing your documents and processed docs
    documents_dir = "./documents"
    processed_dir = "./processed_documents"

    # Check if documents are already in the database
    vector_store = init_vector_store()
    if not vector_store:
        print("Failed to initialize vector store")
        return
    
    try:
        # Try to load existing index
        index = VectorStoreIndex.from_vector_store(vector_store)
        print("Loaded existing document embeddings from database")
        
        # Check if there are new documents to embed
        import os
        if os.path.exists(documents_dir) and any(os.scandir(documents_dir)):
            print("Found new documents to embed")
            index = upload_documents(documents_dir, processed_dir)
            if not index:
                print("Failed to upload new documents")
                return
    except Exception as e:
        print(f"No existing index found, creating new one: {e}")
        # Upload documents (first time embedding)
        index = upload_documents(documents_dir, processed_dir)
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
        # Install pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector SCHEMA public;")
        # Create the table for document embeddings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id UUID PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding vector(1024)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")
        exit(1)

    main()
