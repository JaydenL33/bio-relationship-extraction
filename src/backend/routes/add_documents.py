import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional

from models.structured_response import Relationship
from services.add_document_service import add_relationships_to_neo4j, add_text_document



# Define a Pydantic model for request validation
class Document(BaseModel):
    text: str
    metadata: Optional[dict] = None
    
router = APIRouter()
@router.post("/add_document/")
async def add_document(document: Document = Body(...)):
    if not document.text:
        raise HTTPException(status_code=400, detail="Document text is required")
    if not document.metadata:
        document.metadata = {
            "file_name": "API added document",
            "file_path": "unknown",
            "source": "user_added_document",
            "document_type": "biomedical_text",
            "timestamp": datetime.datetime.now().isoformat(),  
            "process_status": "pending",
        }
    try:
        add_text_document(document.text, document.metadata)
        return {"message": "Document added successfully"}, 201
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Addings a relationship to our Neo4j database
@router.post("/neo4j/add_relationship/")
async def add_relationship(relationships: Relationship = Body(...)):
    try:
        # Assuming you have a function to add a relationship in your service
        await add_relationships_to_neo4j(relationships)
        return {"message": "Relationship added successfully"}, 201
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")