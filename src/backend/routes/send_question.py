from fastapi import APIRouter, FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional

from services.query_documents import query_documents
from services.llm import index


# Define a Pydantic model for request validation
class Question(BaseModel):
    text: str
    
router = APIRouter()
@router.post("/questions/")
async def send_question(question: Question = Body(...)):
    try:
        response = query_documents(question.text, index)
        # Print structured response
        response_dict = response.response.model_dump()
        print(response.response.model_dump_json(indent=2))
        print("\nRelationships:")
        if response_dict["relationships"]:
            print("---------------------")
            for rel in response_dict["relationships"]:
                print(
                    f"{rel['entity1']} {rel['relation']} {rel['entity2']}")
            print("---------------------")
        print("\nExplanation:", response_dict["explanation"])
        print("\nSources:")
        for node in response.source_nodes:
            print(f"- {node.node.metadata.get('file_name', 'Unknown')}: "
                    f"Score: {node.score:.3f}")
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        