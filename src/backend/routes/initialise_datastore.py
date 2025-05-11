
import os
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

from main import query_documents
from services.initalise_vector_store import upload_documents
from services.llm import setup_models


# Define a Pydantic model for request validation
class Question(BaseModel):
    text: str
    

@app.post("/initalise/")
async def send_question(question: Question = Body(...)):
    documents_dir = "./documents"
    processed_dir = "./processed_documents"
    try:
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