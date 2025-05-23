from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, Document
from llama_index.vector_stores.postgres import PGVectorStore
import os
import shutil
import json


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


def upload_documents(directory_path="./documents", processed_dir="./processed_documents"):
    os.makedirs(processed_dir, exist_ok=True)
    try:
        # Process text files for content and JSON files for metadata
        documents = []
        
        # Get all text files
        text_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
        
        for text_file in text_files:
            base_name = os.path.splitext(text_file)[0]
            json_file = f"{base_name}.json"
            text_path = os.path.join(directory_path, text_file)
            json_path = os.path.join(directory_path, json_file)
            
            # Read text content
            with open(text_path, 'r') as f:
                content = f.read()
            
            # Read metadata from JSON if it exists
            metadata = {"file_path": text_path}  # Default metadata with file path
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        json_metadata = json.load(f)
                    metadata.update(json_metadata)  # Add JSON content to metadata
                    # Add json file path to be moved later
                    metadata["json_file_path"] = json_path
                except Exception as e:
                    print(f"Error reading JSON metadata {json_path}: {e}")
            
            # Create document object
            doc = Document(text=content, metadata=metadata)
            documents.append(doc)
        
        if not documents:
            print("No text documents found to embed")
            return False
    except Exception as e:
        print(f"Error loading documents: {e}")
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

        # Move files to processed directory
        for doc in documents:
            file_path = doc.metadata.get("file_path")
            if file_path and os.path.exists(file_path):
                destination = os.path.join(
                    processed_dir, os.path.basename(file_path))
                print(f"Moving {file_path} to {destination}")
                shutil.move(file_path, destination)
            
            # Also move the JSON files
            json_file_path = doc.metadata.get("json_file_path")
            if json_file_path and os.path.exists(json_file_path):
                json_destination = os.path.join(
                    processed_dir, os.path.basename(json_file_path))
                print(f"Moving {json_file_path} to {json_destination}")
                shutil.move(json_file_path, json_destination)
                
        return index
    except Exception as e:
        print(f"Error embedding documents: {e}")
        return False