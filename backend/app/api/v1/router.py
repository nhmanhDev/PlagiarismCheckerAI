"""
API Router - Version 1

Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import corpus, plagiarism, system, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    corpus.router,
    prefix="/v1/corpus",
    tags=["Corpus Management"]
)

api_router.include_router(
    plagiarism.router,
    prefix="/v1/plagiarism",
    tags=["Plagiarism Detection"]
)

api_router.include_router(
    chat.router,
    prefix="/v1/chat",
    tags=["AI Chat"]
)

api_router.include_router(
    system.router,
    prefix="/v1/system",
    tags=["System"]
)
