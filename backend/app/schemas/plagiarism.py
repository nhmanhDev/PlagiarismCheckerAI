"""
Plagiarism Check Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CheckRequest(BaseModel):
    query_text: str = Field(..., min_length=1)
    alpha: float = Field(0.4, ge=0, le=1)
    top_k_lex: int = Field(10, ge=1, le=50)
    top_k_sem: int = Field(10, ge=1, le=50)
    top_n: int = Field(5, ge=1, le=20)
    threshold: float = Field(0.75, ge=0, le=1)
    use_reranker: bool = False


class PlagiarismResult(BaseModel):
    index: int
    text: str
    score_final: float
    score_lexical_raw: Optional[float] = None
    score_semantic_raw: Optional[float] = None
    rerank_score: Optional[float] = None
    hybrid_rerank_score: Optional[float] = None
    is_suspected: bool


class CheckResponse(BaseModel):
    query: str
    results: list[PlagiarismResult]
    alpha: float
    threshold: float
    corpus_id: str
    vietnamese_detected: bool
    method: str = "hybrid"
    reranker_used: bool = False
    device: str
    timestamp: datetime

    class Config:
        from_attributes = True
