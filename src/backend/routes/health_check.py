from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict

router = APIRouter()

@router.get("/health", response_model=Dict[str, str], tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify the API is running properly.
    
    Returns:
        JSONResponse: A simple response with status information
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "message": "API is operational"}
    )