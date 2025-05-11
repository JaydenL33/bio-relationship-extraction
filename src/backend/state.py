from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore


# Global application state
class AppState:
    vector_store: PGVectorStore = None
    index: VectorStoreIndex = None
    initialized: bool = False

# Create singleton instance
app_state = AppState()
