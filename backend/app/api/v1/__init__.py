from fastapi import APIRouter
from app.api.v1.endpoints import corpus, plagiarism, chat

api_router = APIRouter()

api_router.include_router(corpus.router, prefix="/corpus", tags=["corpus"])
api_router.include_router(plagiarism.router, prefix="/plagiarism", tags=["plagiarism"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
