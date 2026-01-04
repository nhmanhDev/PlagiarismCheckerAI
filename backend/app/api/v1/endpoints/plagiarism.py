"""
Plagiarism Detection Endpoints
"""

from fastapi import APIRouter, Form, File, UploadFile
from typing import Optional

from app.schemas.plagiarism import CheckRequest, CheckResponse
from app.services.plagiarism_service import PlagiarismService

router = APIRouter()
plagiarism_service = PlagiarismService()


@router.post("/check", response_model=CheckResponse)
async def check_plagiarism(
    query_text: str = Form(...),
    alpha: float = Form(0.4),
    top_k_lex: int = Form(10),
    top_k_sem: int = Form(10),
    top_n: int = Form(5),
    threshold: float = Form(0.75)
):
    """
    Basic plagiarism check using hybrid retrieval (BM25 + Semantic)
    """
    return await plagiarism_service.check(
        query_text=query_text,
        alpha=alpha,
        top_k_lex=top_k_lex,
        top_k_sem=top_k_sem,
        top_n=top_n,
        threshold=threshold
    )


@router.post("/check-multistage", response_model=CheckResponse)
async def check_plagiarism_multistage(
    query_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    alpha: float = Form(0.4),  
    top_n: int = Form(5),
    threshold: float = Form(0.75),
    use_reranker: bool = Form(True)
):
    """
    Multi-stage plagiarism check with re-ranker.
    
    - **query_text**: Text to check (if not uploading file)
    - **file**: PDF or TXT file (if not providing text)
    - **alpha**: BM25 vs Semantic weight
    - **use_reranker**: Use cross-encoder re-ranking
    """
    if not query_text and not file:
        raise HTTPException(400, "Either query_text or file must be provided")
    
    # Handle file upload
    if file:
        from app.services.document_service import DocumentProcessor
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Extract text from file
        processor = DocumentProcessor()
        try:
            query_text = processor.extract_text_from_bytes(
                file_bytes=file_bytes,
                filename=file.filename,
                clean=True  # Apply Vietnamese text cleaning
            )
        except Exception as e:
            raise HTTPException(400, f"Failed to extract text from file: {str(e)}")
    
    return await plagiarism_service.check_multistage(
        query_text=query_text,
        alpha=alpha,
        top_n=top_n,
        threshold=threshold,
        use_reranker=use_reranker
    )
