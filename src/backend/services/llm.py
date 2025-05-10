from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from models.structured_response import BioMedicalResponse

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

