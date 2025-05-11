from fastapi import APIRouter, FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional

from services.add_document_service import add_text_document



# Define a Pydantic model for request validation
class Document(BaseModel):
    text: str
    metadata: Optional[dict] = None
    
router = APIRouter()
@router.post("/add_document/")
async def add_document(document: Document = Body(...)):
    try:
        add_text_document(document.text, document.metadata)
        return {"message": "Document added successfully"}, 201
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Addings a relationship to our Neo4j database
async def add_relationship():
    try:
        # Assuming you have a function to add a relationship in your service
        # add_relationship_to_neo4j()
        return {"message": "Relationship added successfully"}, 201
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")