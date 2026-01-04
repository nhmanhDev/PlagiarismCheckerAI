"""
System Status Endpoints
"""

from fastapi import APIRouter
import torch

from app.core.config import settings

router = APIRouter()


@router.get("/status")
async def get_system_status():
    """Get system status"""
    try:
        from app.services import vietnamese_service
        vn_available = True
    except:
        vn_available = False
    
    try:
        from app.services import document_service
        pdf_available = True
    except:
        pdf_available = False
    
    try:
        from app.services import reranker_service
        reranker_available = True
    except:
        reranker_available = False
    
    return {
        "status": "ok",
        "device": "CUDA" if torch.cuda.is_available() else "CPU",
        "vietnamese_available": vn_available,
        "pdf_available": pdf_available,
        "reranker_available": reranker_available,
        "version": "2.0.0"
    }
