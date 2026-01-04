"""
Cross-Encoder Re-ranker Service

Implements Stage 3 of multi-stage retrieval pipeline.
Uses cross-encoder to re-rank candidates from hybrid retrieval.
"""

from typing import List, Dict, Any
import numpy as np

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    CrossEncoder = None


class RerankerService:
    """Cross-encoder re-ranker for final stage refinement"""
    
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        """
        Initialize cross-encoder model.
        
        Args:
            model_name: HuggingFace model name for cross-encoder
        """
        if not CROSS_ENCODER_AVAILABLE:
            print("Warning: sentence-transformers not available for re-ranking")
            self.model = None
            return
        
        try:
            print(f"Loading cross-encoder model: {model_name}")
            self.model = CrossEncoder(model_name)
            print("Cross-encoder loaded successfully")
        except Exception as e:
            print(f"Failed to load cross-encoder: {e}")
            self.model = None
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Re-rank candidates using cross-encoder.
        
        Args:
            query: Query text
            candidates: List of candidate results from hybrid retrieval
            top_n: Number of top results to return
        
        Returns:
            Re-ranked list of candidates with updated scores
        """
        if not self.model or not candidates:
            return candidates[:top_n]
        
        try:
            # Build query-document pairs
            pairs = [[query, candidate['text']] for candidate in candidates]
            
            # Get cross-encoder scores
            ce_scores = self.model.predict(pairs)
            
            # Normalize scores to [0, 1]
            ce_scores_norm = self._normalize_scores(ce_scores)
            
            # Update candidates with re-ranker scores
            for idx, candidate in enumerate(candidates):
                candidate['score_reranker'] = float(ce_scores_norm[idx])
                # Combine with hybrid: 70% reranker + 30% hybrid
                candidate['score_final'] = (
                    0.7 * candidate['score_reranker'] + 
                    0.3 * candidate.get('score_final', 0.5)
                )
            
            # Sort by final score
            reranked = sorted(
                candidates,
                key=lambda x: x['score_final'],
                reverse=True
            )
            
            return reranked[:top_n]
            
        except Exception as e:
            print(f"Re-ranking failed: {e}")
            return candidates[:top_n]
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to [0, 1] range"""
        scores = np.array(scores)
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score > min_score:
            normalized = (scores - min_score) / (max_score - min_score)
        else:
            normalized = np.zeros_like(scores)
        
        return np.clip(normalized, 0.0, 1.0)
    
    @property
    def is_available(self) -> bool:
        """Check if re-ranker is available"""
        return self.model is not None
