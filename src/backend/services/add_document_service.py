from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, Document
from llama_index.vector_stores.postgres import PGVectorStore
import os
import shutil

from config import get_neo4j_connection
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

async def add_relationships_to_neo4j(response_dict):
    # Initialize Neo4j driver
    driver = get_neo4j_connection()

    def create_nodes_and_relationships(tx, entity1, relation, entity2):
        # Cypher query to create nodes (if they don't exist) and a relationship
        query = (
            "MERGE (e1:Entity {name: $entity1}) "  # Create or match entity1 node
            "MERGE (e2:Entity {name: $entity2}) "  # Create or match entity2 node
            "MERGE (e1)-[r:RELATION {type: $relation}]->(e2) "  # Create relationship
            "RETURN e1, r, e2"
        )
        tx.run(query, entity1=entity1, entity2=entity2, relation=relation)

    # Process relationships
    if response_dict.get("relationships"):
        print("---------------------")
        with driver.session() as session:
            for rel in response_dict["relationships"]:
                entity1 = rel["entity1"]
                relation = rel["relation"]
                entity2 = rel["entity2"]
                print(f"{entity1} {relation} {entity2}")
                # Execute the Cypher query to add to Neo4j using non-deprecated method
                session.execute_write(create_nodes_and_relationships, entity1, relation, entity2)

    # Close the driver
    driver.close()
