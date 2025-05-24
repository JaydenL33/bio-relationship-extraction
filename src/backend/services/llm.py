from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from services.initalise_vector_store import init_vector_store
from models.structured_response import BioMedicalResponse
from llama_index.core import VectorStoreIndex, Settings, StorageContext
import sys
from state import app_state
# Configuration | This Base URL is used to connect to the Ollama server
# and should be set to the address of the server running the Ollama models.
# For local testing, this is usually http://localhost:11434
# But for WSL, you need to use the IP address of the WSL instance.
# You can check that by running ipconfig in PowerShell and looking for the WSL adapter.
# If you can't figure this out, just ask your instructor or email me.
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
    Settings.embed_model = OllamaEmbedding(
        model_name="bge-m3:latest",
        base_url=base_url
    )
    Settings.llm = Ollama(
        model="deepseek-r1:14b",
        base_url=base_url,
        temperature=0.3,  # Set temperature for more deterministic responses
        # top_p=0.9,  # Set top_p for nucleus sampling
        # verbose=True,  # Enable verbose mode
    ).as_structured_llm(output_cls=BioMedicalResponse)


def initialise_resources(store=None, index=None):
    """Initialize all LLM and vector store resources"""
    try:
        print("Initializing LLM resources...")
        # Setup LLM and embedding models
        setup_models()

        if store:
            # Use provided vector store
            vector_store = store
        else:
            vector_store = init_vector_store()
        if not vector_store:
            print("Failed to initialize vector store")
            return False

        # Create storage context and index
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        if index:
            index = index
        else:
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )

        # Store in global state
        app_state.vector_store = vector_store
        app_state.index = index
        app_state.initialized = True

        print("LLM resources initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing resources: {e}", file=sys.stderr)
        return False


def get_index():
    """Get the vector index, initializing if needed"""
    if not app_state.initialized:
        initialise_resources()
    return app_state.index

