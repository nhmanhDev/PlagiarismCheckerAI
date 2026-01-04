"""
Corpus Manager Module

Handles persistence and management of multiple corpora.
Uses FAISS for vector storage and JSON for metadata.
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None


try:
    from app.core.config import settings
except ImportError:
    # Try relative import as fallback
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from app.core.config import settings


class CorpusManager:
    """Manage multiple corpora with persistence."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize corpus manager.
        
        Args:
            storage_dir: Directory to store corpus data. Uses settings default if None.
        """
        self.storage_dir = storage_dir or settings.CORPUS_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        if not FAISS_AVAILABLE:
            print("Warning: FAISS not installed. Persistence will not work.")
    
    def generate_corpus_id(self) -> str:
        """Generate unique corpus ID."""
        return str(uuid.uuid4())[:8]
    
    def save_corpus(
        self,
        corpus_id: str,
        segments: List[str],
        embeddings: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save corpus to disk.
        
        Args:
            corpus_id: Unique corpus identifier
            segments: List of text segments
            embeddings: Numpy array of embeddings
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            print("Cannot save corpus: FAISS not available")
            return False
        
        try:
            corpus_path = self.storage_dir / corpus_id
            corpus_path.mkdir(exist_ok=True)
            
            # Save embeddings as FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            index.add(embeddings.astype('float32'))
            faiss.write_index(index, str(corpus_path / "embeddings.faiss"))
            
            # Save segments
            with open(corpus_path / "segments.json", 'w', encoding='utf-8') as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
            
            # Save metadata
            meta = metadata or {}
            meta.update({
                "corpus_id": corpus_id,
                "num_segments": len(segments),
                "embedding_dim": dimension,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
            
            with open(corpus_path / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            
            print(f"Corpus '{corpus_id}' saved successfully")
            return True
            
        except Exception as e:
            print(f"Error saving corpus: {e}")
            return False
    
    def load_corpus(self, corpus_id: str) -> Optional[Dict[str, Any]]:
        """
        Load corpus from disk.
        
        Args:
            corpus_id: Unique corpus identifier
            
        Returns:
            Dictionary with 'segments', 'embeddings', 'metadata' or None if failed
        """
        if not FAISS_AVAILABLE:
            print("Cannot load corpus: FAISS not available")
            return None
        
        try:
            corpus_path = self.storage_dir / corpus_id
            
            if not corpus_path.exists():
                print(f"Corpus '{corpus_id}' not found")
                return None
            
            # Load FAISS index
            index = faiss.read_index(str(corpus_path / "embeddings.faiss"))
            embeddings = faiss.vector_to_array(index.reconstruct_n(0, index.ntotal))
            
            # Reshape embeddings
            dimension = index.d
            embeddings = embeddings.reshape(-1, dimension)
            
            # Load segments
            with open(corpus_path / "segments.json", 'r', encoding='utf-8') as f:
                segments = json.load(f)
            
            # Load metadata
            with open(corpus_path / "metadata.json", 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {
                "corpus_id": corpus_id,
                "segments": segments,
                "embeddings": embeddings,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error loading corpus: {e}")
            return None
    
    def list_corpora(self) -> List[Dict[str, Any]]:
        """
        List all saved corpora.
        
        Returns:
            List of corpus metadata dictionaries
        """
        corpora = []
        
        try:
            for corpus_path in self.storage_dir.iterdir():
                if not corpus_path.is_dir():
                    continue
                
                metadata_file = corpus_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        corpora.append(metadata)
            
            # Sort by creation date (newest first)
            corpora.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
        except Exception as e:
            print(f"Error listing corpora: {e}")
        
        return corpora
    
    def delete_corpus(self, corpus_id: str) -> bool:
        """
        Delete a corpus.
        
        Args:
            corpus_id: Unique corpus identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            corpus_path = self.storage_dir / corpus_id
            
            if not corpus_path.exists():
                print(f"Corpus '{corpus_id}' not found")
                return False
            
            # Delete all files in corpus directory
            for file_path in corpus_path.iterdir():
                file_path.unlink()
            
            # Delete directory
            corpus_path.rmdir()
            
            print(f"Corpus '{corpus_id}' deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting corpus: {e}")
            return False
    
    def get_stats(self, corpus_id: str) -> Optional[Dict[str, Any]]:
        """
        Get corpus statistics.
        
        Args:
            corpus_id: Unique corpus identifier
            
        Returns:
            Dictionary with statistics or None if failed
        """
        try:
            corpus_path = self.storage_dir / corpus_id
            
            if not corpus_path.exists():
                return None
            
            # Load metadata
            with open(corpus_path / "metadata.json", 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Calculate additional stats
            stats = {
                "corpus_id": corpus_id,
                "num_segments": metadata.get("num_segments", 0),
                "embedding_dim": metadata.get("embedding_dim", 0),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "name": metadata.get("name", corpus_id),
                "source": metadata.get("source", "unknown"),
                "vietnamese": metadata.get("vietnamese_detected", False)
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    def update_metadata(self, corpus_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update corpus metadata.
        
        Args:
            corpus_id: Unique corpus identifier
            updates: Dictionary of metadata updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            corpus_path = self.storage_dir / corpus_id
            metadata_file = corpus_path / "metadata.json"
            
            if not metadata_file.exists():
                return False
            
            # Load existing metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Update
            metadata.update(updates)
            metadata["updated_at"] = datetime.now().isoformat()
            
            # Save
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error updating metadata: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("=== Corpus Manager Test ===\n")
    
    manager = CorpusManager()
    print(f"Storage directory: {manager.storage_dir}")
    print(f"FAISS available: {FAISS_AVAILABLE}")
    
    # List existing corpora
    corpora = manager.list_corpora()
    print(f"\nExisting corpora: {len(corpora)}")
    for corpus in corpora:
        print(f"  - {corpus['corpus_id']}: {corpus.get('name', 'Unnamed')} ({corpus['num_segments']} segments)")
