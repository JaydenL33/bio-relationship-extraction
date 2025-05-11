from fastapi import APIRouter
from .health_check import router as health_router
from .send_question import router as question_router

# Create a main router that includes all sub-routers
router = APIRouter()

# Include all the individual routers
router.include_router(health_router)
router.include_router(question_router)
