import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from services.initalise_vector_store import init_vector_store, upload_documents
from services.llm import initialise_resources
from state import app_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources before the app starts
    print("Initializing application resources...")
    if not app_state.initialized:
        success = initialise_resources()
        if not success:
            print("WARNING: Failed to initialize resources during startup")
    yield
    # Cleanup code would go here if needed
    print("Shutting down application...")


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
    # Initialize resources early to avoid timing issues
    if not app_state.initialized:
        initialise_resources()

if __name__ == "__main__":
    # Initialize before starting the server
    main()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

