"""
Chat API Endpoints

Provides AI-powered explanations for detection results
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.chatbot_service import get_chatbot_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Request for chat explanation"""
    query_text: str
    detection_results: List[Dict]
    user_question: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chatbot"""
    response: str
    model: str = "gemini-pro"
    available: bool = True


@router.post("/explain", response_model=ChatResponse)
async def explain_results(request: ChatRequest):
    """
    Get AI explanation for plagiarism detection results.
    
    - **query_text**: The original text that was checked for plagiarism
    - **detection_results**: Results from the plagiarism check
    - **user_question**: Optional specific question from the user
    
    Returns AI-generated explanation in Vietnamese.
    """
    chatbot = get_chatbot_service()
    
    if not chatbot.is_available():
        return ChatResponse(
            response="Chatbot AI hiện chưa được cấu hình. Vui lòng thêm GEMINI_API_KEY vào file .env",
            available=False
        )
    
    try:
        explanation = await chatbot.explain_result(
            query_text=request.query_text,
            detection_results=request.detection_results,
            user_question=request.user_question
        )
        
        return ChatResponse(
            response=explanation,
            available=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot error: {str(e)}"
        )


@router.get("/status")
async def chatbot_status():
    """Check if chatbot is available"""
    chatbot = get_chatbot_service()
    return {
        "available": chatbot.is_available(),
        "model": "gemini-pro" if chatbot.is_available() else None
    }
