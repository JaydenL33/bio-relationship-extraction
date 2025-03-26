from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os

# Initialize FastAPI app
app = FastAPI(title="RAG API with LlamaIndex")

# Pydantic model for request body
class QueryRequest(BaseModel):
    query: str

# Set up LlamaIndex embedding model (BAAI/bge-small-en-v1.5)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Load documents and create index (assuming a 'data' folder exists)
def load_index():
    data_dir = "./data"
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        raise ValueError("Data directory is empty or does not exist.")
    documents = SimpleDirectoryReader(data_dir).load_data()
    return VectorStoreIndex.from_documents(documents)

# Global index variable (loaded once at startup)
index = None

@app.on_event("startup")
async def startup_event():
    global index
    try:
        index = load_index()
        print("Index loaded successfully.")
    except Exception as e:
        print(f"Failed to load index: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}

# Query endpoint
@app.post("/query")
async def query_documents(request: QueryRequest):
    if index is None:
        raise HTTPException(status_code=500, detail="Index not initialized.")
    try:
        query_engine = index.as_query_engine()
        response = query_engine.query(request.query)
        return {"query": request.query, "response": str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)