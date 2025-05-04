from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, PromptTemplate, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
import psycopg2
import os
import shutil
import uuid

custom_prompt = PromptTemplate(
    """
    System Prompt:
    You are a precise and knowledgeable assistant specializing in bio-medical queries. Use the provided context to answer the query in a structured manner, extracting as much relevant information as possible.
    You are embedded within a system with access to a database of bio-medical documents. Your task is to extract relevant information from these documents based on user queries.
    You will be provided with a context string containing bio-medical information and a user query. Your goal is to identify relationships between entities mentioned in the context and provide answers according to the instructions.
    Do not provide any information about yourself, your capabilities, or the system. Focus solely on the context and query provided.

    **Instructions:**
    1. For queries about relationships between entities (e.g., organisms, chemicals, proteins), provide answers using only the following relationship types, if applicable:
       - ISOLATED_FROM: A chemical or protein is isolated from an organism.
       - METABOLITE_OF: A chemical is a metabolite of another chemical.
       - PRODUCES: An organism produces a chemical or protein.
       - DEGRADED_BY: A chemical is broken down or degraded by an organism.
       - BIOSYNTHESIZED_BY: An organism synthesizes a chemical via metabolic pathways.
       - INHIBITS: A chemical produced by an organism inhibits another organism.
       - PRECURSOR_OF: A chemical is a precursor in the biosynthesis of another chemical.
       - UPTAKEN_BY: An organism takes up a chemical for metabolic use.
       - MODIFIES: An organism chemically modifies a metabolite to produce a derivative.
       - SEQUESTERS: An organism accumulates or stores a chemical without metabolizing it.
       - CONTAINS: A chemical is contained within an organism.
       These relationships are to be extracted for a Neo4j graph database. Use exact entity names from the context.
    2. Format the answer as a list of relationships using exact entity names (avoid generic terms like "bacteria" or "marine organisms"):
       ---------------------
       entity1 RELATION entity2
       ---------------------
       Use this format for all relationship queries. For non-relationship queries (e.g., a chemical's function), provide a concise natural language answer.
    3. **Link relationships as pairs or triplets where applicable**:
       - If an entity is isolated from an organism (`ISOLATED_FROM`), check if the same organism produces it (`PRODUCES`) and include both relationships as a linked pair.
       - If a chemical is a metabolite (`METABOLITE_OF`) or precursor (`PRECURSOR_OF`), check for related biosynthetic relationships (e.g., `BIOSYNTHESIZED_BY`, `PRODUCES`) to form triplets where possible.
       - Ensure relationships are grouped logically to reflect their interconnectedness (e.g., `entity1 PRODUCES entity2`, `entity2 ISOLATED_FROM entity1`).
    4. Follow the relationships with a concise natural language explanation summarizing the results, emphasizing the linked relationships.
    5. If the query’s answer or relationship type is not found in the context, respond with: "Not found in the provided context."
    6. Ensure responses are clear, specific, and aligned with the context, prioritizing brevity without sacrificing accuracy.
    7. Always surround relationships with:
       ---------------------
       ---------------------

    **Examples:**

    **Example 1:**
    Query: From what organisms is neomycin isolated?
    Answer:
    ---------------------
    neomycin ISOLATED_FROM Streptomyces rimosus forma paromomycinus
    Streptomyces rimosus forma paromomycinus PRODUCES neomycin
    neomycin ISOLATED_FROM Streptomyces fradiae
    Streptomyces fradiae PRODUCES neomycin
    neomycin METABOLITE_OF neamine
    ---------------------
    Explanation: Neomycin is isolated from and produced by *Streptomyces rimosus forma paromomycinus* and *Streptomyces fradiae*. It is also a metabolite of neamine.

    **Example 2:**
    Query: What organism is HhH-GPD isolated from?
    Answer:
    ---------------------
    HhH-GPD ISOLATED_FROM Saccharolobus islandicus
    Saccharolobus islandicus PRODUCES HhH-GPD
    ---------------------
    Explanation: HhH-GPD is isolated from and produced by *Saccharolobus islandicus*.

    **Example 3:**
    Query: What is penicillin a metabolite of?
    Answer:
    ---------------------
    penicillin METABOLITE_OF benzylpenicillanic acid
    Penicillium chrysogenum BIOSYNTHESIZED_BY penicillin
    ---------------------
    Explanation: Penicillin is a metabolite of benzylpenicillanic acid and biosynthesized by *Penicillium chrysogenum*.

    **Example 4:**
    Query: What produces tetracycline?
    Answer:
    ---------------------
    Streptomyces aureofaciens PRODUCES tetracycline
    tetracycline ISOLATED_FROM Streptomyces aureofaciens
    ---------------------
    Explanation: Tetracycline is produced by and isolated from *Streptomyces aureofaciens*.

    **Example 5:**
    Query: What organism produces insulin?
    Answer:
    Not found in the provided context.

    **Context:**
    ---------------------
    {context_str}
    ---------------------

    **Query:**
    ---------------------
    {query_str}
    ---------------------
    """
)

# Ollama API base URL
base_url = "http://172.20.80.1:11434"

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
        base_url=base_url
    )

    # LLM model (deepseek-r1)
    Settings.llm = Ollama(
        model="deepseek-r1:14b",
        base_url=base_url
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
        # Create storage context with PGVectorStore
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index with documents and storage context
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        
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
        )
    query_engine.update_prompts({"response_synthesizer:text_qa_template": custom_prompt})

    # Execute query and return response
    response = query_engine.query(query_str)
    return response

def main():
    # Setup models
    setup_models()

    # Directory containing your documents and processed docs
    documents_dir = "./documents"
    processed_dir = "./processed_documents"

    # Initialize vector store
    vector_store = init_vector_store()
    if not vector_store:
        print("Failed to initialize vector store")
        return
    
    try:
        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Try to load existing index
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        print("Loaded existing document embeddings from database")
        
        # Check if there are new documents to embed
        if os.path.exists(documents_dir) and any(os.scandir(documents_dir)):
            print("Found new documents to embed")
            new_index = upload_documents(documents_dir, processed_dir)
            if new_index:
                index = new_index
            else:
                print("Failed to upload new documents")
    except Exception as e:
        print(f"No existing index found, creating new one: {e}")
        # Upload documents (first time embedding)
        index = upload_documents(documents_dir, processed_dir)
        if not index:
            print("Failed to upload documents")
            return
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