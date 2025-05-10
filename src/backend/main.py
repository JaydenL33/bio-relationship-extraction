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

# Initialise Ollama models

def setup_models():
    Settings.embed_model = OllamaEmbedding(
        model_name="bge-m3:latest",
        base_url=base_url
    )
    Settings.llm = Ollama(
        model="deepseek-r1:14b",
        base_url=base_url,
        
    ).as_structured_llm(output_cls=BioMedicalResponse)

    # Settings.llm = Ollama(
    #     model="deepseek-r1:14b",
    #     base_url=base_url,
    # ).as_structured_llm(output_cls=BioMedicalResponse)
    Settings.pydantic_program_mode

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
            embed_dim=1024,
            hybrid_search=True,
            text_search_config="english",
        )
        return vector_store
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Upload and embed documents


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

# Query the database with structured output


def query_documents(query_str: str, index: VectorStoreIndex):
    # Define system prompt for structured output
    relationship_types_str = ", ".join([r.value for r in RelationshipType])

    # Define the template string with relationship types inserted
    system_prompt = PromptTemplate(
        f"""
        You are a precise and knowledgeable assistant specializing in bio-medical queries. Use the provided context to answer the query in a structured JSON format, extracting relevant information as per the instructions.

        **Instructions:**
        1. Extract relationships between entities (e.g., organisms, chemicals, proteins) using only the following relationship types:
        {relationship_types_str}
        2. Use exact entity names from the context, avoiding generic terms.
        3. Link relationships as pairs or triplets where applicable:
        - If an entity is isolated from an organism (`ISOLATED_FROM`), check if the same organism produces it (`PRODUCES`).
        - If a chemical is a metabolite (`METABOLITE_OF`) or precursor (`PRECURSOR_OF`), check for related biosynthetic relationships.
        4. Provide a concise natural language explanation summarizing the results.
        5. If the query’s answer or relationship type is not found, return an empty list of relationships and an explanation stating: "Not found in the provided context."
        6. Output the response as a JSON object conforming to the provided schema.

        **Context:**
        {{context_str}}

        **Query:**
        {{query_str}}
        """
    )

    # Create query engine with structured output
    vector_retriever = index.as_retriever(
        vector_store_query_mode="default",
        similarity_top_k=5,
    )
    text_retriever = index.as_retriever(
        vector_store_query_mode="sparse",
        similarity_top_k=5,
    )
    retriever = QueryFusionRetriever(
        [vector_retriever, text_retriever],
        similarity_top_k=5,
        num_queries=1,
        mode="relative_score",
        use_async=False,
    )

    response_synthesizer = CompactAndRefine()
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
    )

    query_engine.update_prompts(
        {"response_synthesizer:text_qa_template": system_prompt}
    )

    # Execute query and return structured response
    response = query_engine.query(query_str)
    return response


def main():
    setup_models()
    documents_dir = "./documents"
    processed_dir = "./processed_documents"

    vector_store = init_vector_store()
    if not vector_store:
        print("Failed to initialize vector store")
        return

    try:
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        print("Loaded existing document embeddings from database")

        if os.path.exists(documents_dir) and any(os.scandir(documents_dir)):
            print("Found new documents to embed")
            new_index = upload_documents(documents_dir, processed_dir)
            if new_index:
                index = new_index
            else:
                print("Failed to upload new documents")
    except Exception as e:
        print(f"No existing index found, creating new one: {e}")
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
            # Print structured response
            response_dict = response.response.model_dump()
            print(response.response.model_dump_json(indent=2))
            print("\nRelationships:")
            if response_dict["relationships"]:
                print("---------------------")
                for rel in response_dict["relationships"]:
                    print(
                        f"{rel['entity1']} {rel['relation']} {rel['entity2']}")
                print("---------------------")
            print("\nExplanation:", response_dict["explanation"])
            print("\nSources:")
            for node in response.source_nodes:
                print(f"- {node.node.metadata.get('file_name', 'Unknown')}: "
                      f"Score: {node.score:.3f}")
        except Exception as e:
            print(f"Error processing query: {e}")


if __name__ == "__main__":
    main()
