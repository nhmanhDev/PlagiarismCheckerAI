"""
Corpus Service - Simplified Business Logic

Handles corpus operations without complex dependencies
"""

from fastapi import UploadFile, HTTPException
from typing import Optional
import json
import uuid
from datetime import datetime
from pathlib import Path

class CorpusService:
    def __init__(self):
        self.data_dir = Path("../data/corpora")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.active_corpus_id = None
    
    async def create_corpus(
        self,
        name: str,
        corpus_text: Optional[str] = None,
        file: Optional[UploadFile] = None,
        split_mode: str = "auto"
    ):
        """Create a new corpus from text"""
        if not corpus_text and not file:
            raise HTTPException(400, "Either corpus_text or file must be provided")
        
        # For now, only support text (file upload can be added later)
        if file:
            raise HTTPException(501, "File upload not yet implemented. Please use text input.")
        
        # Generate corpus ID
        corpus_id = f"corpus_{str(uuid.uuid4())[:8]}"
        corpus_path = self.data_dir / corpus_id
        corpus_path.mkdir(exist_ok=True)
        
        # Split text into segments (simple split by paragraphs or sentences)
        segments = self._split_text(corpus_text, split_mode)
        
        # Save segments
        with open(corpus_path / "segments.json", 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = {
            "id": corpus_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "segment_count": len(segments),
            "split_mode": split_mode
        }
        
        with open(corpus_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return {
            "id": corpus_id,
            "name": name,
            "created_at": metadata["created_at"],
            "segment_count": len(segments),
            "is_active": False
        }
    
    def _split_text(self, text: str, mode: str = "auto") -> list[str]:
        """Split text into segments"""
        if mode == "sentence":
            # Simple sentence split
            import re
            segments = re.split(r'[.!?]+', text)
            segments = [s.strip() for s in segments if s.strip()]
        elif mode == "paragraph":
            # Split by double newlines
            segments = [p.strip() for p in text.split('\n\n') if p.strip()]
        else:  # auto
            # Split by single newlines
            segments = [line.strip() for line in text.split('\n') if line.strip()]
        
        return segments
    
    async def list_corpora(self):
        """List all corpora"""
        corpora = []
        
        if not self.data_dir.exists():
            return {"corpora": [], "active_corpus_id": None}
        
        for corpus_path in self.data_dir.iterdir():
            if not corpus_path.is_dir():
                continue
            
            metadata_file = corpus_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    metadata["is_active"] = metadata["id"] == self.active_corpus_id
                    corpora.append(metadata)
        
        # Sort by creation date (newest first)
        corpora.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {
            "corpora": corpora,
            "active_corpus_id": self.active_corpus_id
        }
    
    async def get_corpus(self, corpus_id: str):
        """Get corpus by ID"""
        corpus_path = self.data_dir / corpus_id
        metadata_file = corpus_path / "metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(404, f"Corpus {corpus_id} not found")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            metadata["is_active"] = corpus_id == self.active_corpus_id
            return metadata
    
    async def activate_corpus(self, corpus_id: str):
        """Activate a corpus"""
        corpus_path = self.data_dir / corpus_id
        
        if not corpus_path.exists():
            raise HTTPException(404, f"Corpus {corpus_id} not found")
        
        self.active_corpus_id = corpus_id
        
        # Save to file so other services can access
        active_file = Path("../data/active_corpus.txt")
        active_file.parent.mkdir(parents=True, exist_ok=True)
        active_file.write_text(corpus_id)
        
        return corpus_id
    
    async def delete_corpus(self, corpus_id: str):
        """Delete a corpus"""
        corpus_path = self.data_dir / corpus_id
        
        if not corpus_path.exists():
            raise HTTPException(404, f"Corpus {corpus_id} not found")
        
        # Delete all files
        for file_path in corpus_path.iterdir():
            file_path.unlink()
        
        # Delete directory
        corpus_path.rmdir()
        
        if self.active_corpus_id == corpus_id:
            self.active_corpus_id = None
