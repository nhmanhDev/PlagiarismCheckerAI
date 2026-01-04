"""
Corpus Management Endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional

from app.schemas.corpus import CorpusResponse, CorpusListResponse
from app.services.corpus_service import CorpusService

router = APIRouter()
corpus_service = CorpusService()


@router.post("/", response_model=CorpusResponse)
async def create_corpus(
    name: str = Form(...),
    corpus_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    split_mode: str = Form("auto")
):
    """Create a new corpus from text or file"""
    if not corpus_text and not file:
        raise HTTPException(400, "Either corpus_text or file must be provided")
    
    return await corpus_service.create_corpus(
        name=name,
        corpus_text=corpus_text,
        file=file,
        split_mode=split_mode
    )


@router.get("/", response_model=CorpusListResponse)
async def list_corpora():
    """List all corpora"""
    return await corpus_service.list_corpora()


@router.get("/{corpus_id}", response_model=CorpusResponse)
async def get_corpus(corpus_id: str):
    """Get corpus by ID"""
    return await corpus_service.get_corpus(corpus_id)


@router.post("/{corpus_id}/activate")
async def activate_corpus(corpus_id: str):
    """Activate a corpus"""
    await corpus_service.activate_corpus(corpus_id)
    return {"message": "Corpus activated", "corpus_id": corpus_id}


@router.delete("/{corpus_id}")
async def delete_corpus(corpus_id: str):
    """Delete a corpus"""
    await corpus_service.delete_corpus(corpus_id)
    return {"message": "Corpus deleted", "corpus_id": corpus_id}
