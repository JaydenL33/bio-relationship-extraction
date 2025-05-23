from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, Document
from llama_index.vector_stores.postgres import PGVectorStore
import os
import shutil

from config import get_neo4j_connection
from models.structured_response import Relationship
from services.initalise_vector_store import init_vector_store


def add_text_document(text, metadata=None) -> bool:
    """
    Add a text document directly to the vector store
    
    Args:
        text (str): The text content to be embedded
        metadata (dict, optional): Metadata for the document
    
    Returns:
        VectorStoreIndex or False: The index if successful, False otherwise
    """
    if not text:
        print("No text provided to embed")
        return False
        
    vector_store = init_vector_store()
    if not vector_store:
        return False
        
    try:
        # Create a Document object from the text
        document = Document(text=text, metadata=metadata or {})
        
        # Create storage context and index
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex.from_documents(
            [document],
            storage_context=storage_context,
            show_progress=True
        )
        print("Successfully embedded text document")
        return True
    except Exception as e:
        print(f"Error embedding text document: {e}")
        return False