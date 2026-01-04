"""
Plagiarism Detection Service - With Real Retrieval Logic

Integrates BM25 + Semantic Embeddings + Re-ranker
"""

from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from vietnamese_processor import VietnameseProcessor
    VN_PROCESSOR_AVAILABLE = True
except:
    try:
        from backend.app.services.vietnamese_processor import VietnameseProcessor
        VN_PROCESSOR_AVAILABLE = True
    except:
        VN_PROCESSOR_AVAILABLE = False
        VietnameseProcessor = None

try:
    from reranker_service import RerankerService
    RERANKER_AVAILABLE = True
except:
    try:
        from backend.app.services.reranker_service import RerankerService
        RERANKER_AVAILABLE = True
    except:
        RERANKER_AVAILABLE = False
        RerankerService = None

class PlagiarismService:
    def __init__(self):
        self.data_dir = Path("../data/corpora")
        self.active_corpus_file = Path("../data/active_corpus.txt")
        
        # Initialize models
        print("Loading embedding model...")
        self.embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Vietnamese processor
        if VN_PROCESSOR_AVAILABLE and VietnameseProcessor:
            try:
                self.vn_processor = VietnameseProcessor()
            except:
                self.vn_processor = None
        else:
            self.vn_processor = None
        
        # Re-ranker (Stage 3)
        if RERANKER_AVAILABLE and RerankerService:
            try:
                self.reranker = RerankerService()
                print(f"Re-ranker available: {self.reranker.is_available}")
            except:
                self.reranker = None
        else:
            self.reranker = None
        
        # Cache for corpus data
        self.corpus_cache = {}
    
    def _get_active_corpus_id(self) -> Optional[str]:
        """Get currently active corpus ID"""
        if self.active_corpus_file.exists():
            return self.active_corpus_file.read_text().strip()
        return None
    
    def _load_corpus(self, corpus_id: str) -> Dict[str, Any]:
        """Load and cache corpus data"""
        if corpus_id in self.corpus_cache:
            return self.corpus_cache[corpus_id]
        
        segments_file = self.data_dir / corpus_id / "segments.json"
        if not segments_file.exists():
            raise HTTPException(404, f"Corpus {corpus_id} segments not found")
        
        with open(segments_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        
        # Process segments for Vietnamese if available
        processed_segments = segments
        if self.vn_processor:
            try:
                processed_segments = [self.vn_processor.process(s) for s in segments]
            except:
                pass
        
        # Create BM25 index
        tokenized_corpus = [seg.split() for seg in processed_segments]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Create embeddings
        print(f"Creating embeddings for {len(segments)} segments...")
        embeddings = self.embed_model.encode(segments, convert_to_numpy=True, show_progress_bar=False)
        
        corpus_data = {
            "segments": segments,
            "processed_segments": processed_segments,
            "bm25": bm25,
            "embeddings": embeddings
        }
        
        self.corpus_cache[corpus_id] = corpus_data
        return corpus_data
    
    def _hybrid_rank(
        self,
        query: str,
        corpus_data: Dict[str, Any],
        alpha: float = 0.4,
        top_k_lex: int = 10,
        top_k_sem: int = 10,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Hybrid BM25 + Semantic ranking"""
        segments = corpus_data["segments"]
        bm25 = corpus_data["bm25"]
        embeddings = corpus_data["embeddings"]
        
        # Process query
        processed_query = query
        if self.vn_processor:
            try:
                processed_query = self.vn_processor.process(query)
            except:
                pass
        
        # BM25 scores
        query_tokens = processed_query.split()
        bm25_scores = bm25.get_scores(query_tokens)
        
        # Normalize BM25 scores to [0, 1]
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 and max(bm25_scores) > 0 else 1.0
        min_bm25 = min(bm25_scores) if len(bm25_scores) > 0 else 0.0
        
        if max_bm25 > min_bm25:
            bm25_scores_norm = (bm25_scores - min_bm25) / (max_bm25 - min_bm25)
        else:
            bm25_scores_norm = np.zeros_like(bm25_scores)
        
        # Semantic scores
        query_embedding = self.embed_model.encode([query], convert_to_numpy=True)[0]
        
        # Cosine similarity (can be negative!)
        semantic_scores = np.dot(embeddings, query_embedding) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Normalize semantic scores from [-1, 1] to [0, 1]
        semantic_scores_norm = (semantic_scores + 1.0) / 2.0
        # Clip to ensure [0, 1] range
        semantic_scores_norm = np.clip(semantic_scores_norm, 0.0, 1.0)
        
        # Hybrid scores (guaranteed [0, 1])
        hybrid_scores = alpha * bm25_scores_norm + (1 - alpha) * semantic_scores_norm
        
        # Get top results
        top_indices = np.argsort(hybrid_scores)[::-1][:top_n]
        
        results = []
        for idx in top_indices:
            idx = int(idx)
            results.append({
                "index": idx,
                "text": segments[idx],
                "score_final": float(hybrid_scores[idx]),
                "score_lexical_raw": float(bm25_scores_norm[idx]),
                "score_semantic_raw": float(semantic_scores_norm[idx]),
                "is_suspected": float(hybrid_scores[idx]) > 0.7
            })
        
        return results
    
    async def check(
        self,
        query_text: str,
        alpha: float = 0.4,
        top_k_lex: int = 10,
        top_k_sem: int = 10,
        top_n: int = 5,
        threshold: float = 0.75
    ):
        """Real plagiarism check with BM25 + Semantic"""
        corpus_id = self._get_active_corpus_id()
        
        if not corpus_id:
            raise HTTPException(400, "Chưa có kho tài liệu nào được kích hoạt. Vui lòng kích hoạt một kho tài liệu trước.")
        
        # Load corpus
        corpus_data = self._load_corpus(corpus_id)
        
        # Detect Vietnamese
        vietnamese_detected = True  # Default to True for Vietnamese system
        if self.vn_processor and hasattr(self.vn_processor, 'is_vietnamese'):
            try:
                vietnamese_detected = self.vn_processor.is_vietnamese(query_text)
            except:
                # Fallback: simple char detection
                vn_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
                vietnamese_detected = any(c in query_text.lower() for c in vn_chars)
        
        # Hybrid ranking
        results = self._hybrid_rank(
            query=query_text,
            corpus_data=corpus_data,
            alpha=alpha,
            top_k_lex=top_k_lex,
            top_k_sem=top_k_sem,
            top_n=top_n
        )
        
        # Apply threshold
        for result in results:
            result["is_suspected"] = result["score_final"] > threshold
        
        return {
            "query": query_text,
            "results": results,
            "alpha": alpha,
            "threshold": threshold,
            "corpus_id": corpus_id,
            "vietnamese_detected": vietnamese_detected,
            "method": "hybrid",
            "reranker_used": False,
            "device": "CPU",
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_multistage(
        self,
        query_text: str,
        alpha: float = 0.4,
        top_n: int = 5,
        threshold: float = 0.75,
        use_reranker: bool = True
    ):
        """
        Multi-stage plagiarism check with re-ranking.
        
        Pipeline:
        1. BM25 retrieval (lexical)
        2. Semantic retrieval (dense)
        3. Cross-encoder re-ranking (optional)
        """
        # Stages 1 & 2: Get candidates from hybrid retrieval
        candidates_result = await self.check(
            query_text=query_text,
            alpha=alpha,
            top_n=20,  # Get more candidates for re-ranking
            threshold=threshold
        )
        
        candidates = candidates_result['results']
        
        # Stage 3: Re-ranking
        reranker_used = False
        if use_reranker and self.reranker and self.reranker.is_available:
            try:
                candidates = self.reranker.rerank(
                    query=query_text,
                    candidates=candidates,
                    top_n=top_n
                )
                reranker_used = True
            except Exception as e:
                print(f"Re-ranking failed, using hybrid results: {e}")
                candidates = candidates[:top_n]
        else:
            candidates = candidates[:top_n]
        
        # Apply threshold
        for result in candidates:
            result["is_suspected"] = result["score_final"] > threshold
        
        return {
            "query": query_text,
            "results": candidates,
            "alpha": alpha,
            "threshold": threshold,
            "corpus_id": candidates_result['corpus_id'],
            "vietnamese_detected": candidates_result['vietnamese_detected'],
            "method": "multi-stage",
            "reranker_used": reranker_used,
            "device": "CPU",
            "timestamp": datetime.now().isoformat()
        }
