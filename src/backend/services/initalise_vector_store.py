from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, PromptTemplate, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
import os
import shutil
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from models.structured_response import BioMedicalResponse, RelationshipType
from llama_index.core.prompts import PromptTemplate
from llama_index.core.output_parsers import PydanticOutputParser

# Database configuration | Modify this for your database
DB_CONFIG = {
    "dbname": "vector_db",
    "user": "pgvector_user",
    "password": "SuperSecretTestPassword",
    "host": "localhost",
    "port": "5432"
}


def init_vector_store():
    try:
        vector_store = PGVectorStore.from_params(
            database=DB_CONFIG["dbname"],
            host=DB_CONFIG["host"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            table_name="document_embeddings",
            embed_dim=1024,
            hybrid_search=True,
            text_search_config="english",
        )
        return vector_store
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def upload_documents(directory_path, processed_dir="./processed_documents"):
    os.makedirs(processed_dir, exist_ok=True)
    documents = SimpleDirectoryReader(directory_path).load_data()

    if not documents:
        print("No documents found to embed")
        return False

    vector_store = init_vector_store()
    if not vector_store:
        return False

    try:
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        print(f"Successfully embedded {len(documents)} documents")

        for doc in documents:
            file_path = doc.metadata.get("file_path")
            if file_path and os.path.exists(file_path):
                destination = os.path.join(
                    processed_dir, os.path.basename(file_path))
                print(f"Moving {file_path} to {destination}")
                shutil.move(file_path, destination)
        return index
    except Exception as e:
        print(f"Error embedding documents: {e}")
        return False
