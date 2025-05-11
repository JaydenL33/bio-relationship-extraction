from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from services.initalise_vector_store import init_vector_store
from models.structured_response import BioMedicalResponse
from llama_index.core import VectorStoreIndex, Settings, StorageContext

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
        
    ).as_structured_llm(output_cls=BioMedicalResponse)


vector_store = init_vector_store()
if not vector_store:
    print("Failed to initialize vector store")

storage_context = StorageContext.from_defaults(
    vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)