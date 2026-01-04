"""
Corpus Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CorpusBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class CorpusCreate(CorpusBase):
    corpus_text: Optional[str] = None
    split_mode: str = "auto"


class CorpusResponse(CorpusBase):
    id: str
    created_at: datetime
    segment_count: int
    is_active: bool = False

    class Config:
        from_attributes = True


class CorpusListResponse(BaseModel):
    corpora: list[CorpusResponse]
    active_corpus_id: Optional[str] = None
