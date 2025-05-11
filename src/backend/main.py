import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from services.initalise_vector_store import init_vector_store, upload_documents
from services.llm import setup_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize models and vector stores on startup
    await setup_models()
    await upload_documents()
    yield


app = FastAPI(
    title="Bio Relationship Extraction API",
    description="API for extracting relationships from biomedical data",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Bio Relationship Extraction API"}

def main():
    # This function can be used for non-API initialization if needed
    pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

