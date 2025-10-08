from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import pipeline
import torch
import uvicorn
import os
import re
from typing import List, Dict, Any, Tuple

# Lexical retrieval
try:
	from rank_bm25 import BM25Okapi
except Exception:
	BM25Okapi = None  # type: ignore

# Semantic retrieval
try:
	from sentence_transformers import SentenceTransformer
except Exception:
	SentenceTransformer = None  # type: ignore

import numpy as np

APP_TITLE = "AI Plagiarism Checker"
MODEL_ID = "jpwahle/longformer-base-plagiarism-detection"

app = FastAPI(title=APP_TITLE)

# Static and templates setup
if not os.path.isdir("static"):
	os.makedirs("static", exist_ok=True)
if not os.path.isdir("templates"):
	os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_device_index() -> int:
	return 0 if torch.cuda.is_available() else -1


def get_device_name() -> str:
	return "cuda" if torch.cuda.is_available() else "cpu"


def load_pipe():
	# Lazy load to speed up startup
	device = get_device_index()
	return pipeline(
		"text-classification",
		model=MODEL_ID,
		device=device,
	)


# Cache the pipeline in app state
pipe = None
embed_model = None
bm25_index = None
corpus_segments: List[str] = []
corpus_embeddings: np.ndarray | None = None


def ensure_pipe():
	global pipe
	if pipe is None:
		pipe = load_pipe()
	return pipe


def preprocess_text(text: str) -> str:
	"""Normalize text: lowercase, collapse whitespace, keep basic punctuation."""
	text = text.lower()
	# Remove special characters except basic punctuation and Vietnamese diacritics kept as-is
	text = re.sub(r"[^\w\s\.,;:!?()'\-–—”“""’áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]", " ", text)
	text = re.sub(r"\s+", " ", text).strip()
	return text


def split_into_segments(text: str, by: str = "auto", max_len: int = 512) -> List[str]:
	"""Split text into sentences or paragraphs for fine-grained comparison.

	by: 'sentence' | 'paragraph' | 'auto'
	max_len: approximate char length cap per segment to avoid overly long pieces
	"""
	clean = preprocess_text(text)
	segments: List[str]
	if by == "paragraph":
		segments = [p.strip() for p in re.split(r"\n{2,}|\r\n{2,}", clean) if p.strip()]
	elif by == "sentence":
		segments = [s.strip() for s in re.split(r"(?<=[\.!?])\s+", clean) if s.strip()]
	else:
		# auto: prefer sentences; fallback paragraphs if very short
		sentences = [s.strip() for s in re.split(r"(?<=[\.!?])\s+", clean) if s.strip()]
		segments = sentences if len(sentences) >= 1 else [clean]
	# Soft chunking if too long
	result: List[str] = []
	for s in segments:
		if len(s) <= max_len:
			result.append(s)
		else:
			for i in range(0, len(s), max_len):
				piece = s[i:i+max_len].strip()
				if piece:
					result.append(piece)
	return result


def ensure_embed_model(model_id: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
	global embed_model
	if embed_model is None:
		device = 0 if torch.cuda.is_available() else -1
		# SentenceTransformer handles device internally via .to
		embed_model = SentenceTransformer(model_id)
		if device == 0:
			embed_model = embed_model.to("cuda")
	return embed_model


def build_bm25_index(segments: List[str]):
	global bm25_index
	if BM25Okapi is None:
		raise HTTPException(status_code=500, detail="BM25 dependency missing. Install rank-bm25.")
	# Tokenize naively by whitespace
	tokenized = [seg.split() for seg in segments]
	bm25_index = BM25Okapi(tokenized)
	return bm25_index


def lexical_search(query: str, k: int = 5) -> List[Tuple[int, float]]:
	"""Return list of (segment_index, bm25_score)."""
	if bm25_index is None or not corpus_segments:
		raise HTTPException(status_code=400, detail="BM25 index not built. Upload or set corpus first.")
	q_tokens = query.split()
	scores = bm25_index.get_scores(q_tokens)
	# Top-k indices by score
	idxs = np.argsort(scores)[::-1][:k]
	return [(int(i), float(scores[int(i)])) for i in idxs]


def semantic_search(query: str, k: int = 5) -> List[Tuple[int, float]]:
	"""Return list of (segment_index, cosine_similarity)."""
	if SentenceTransformer is None:
		raise HTTPException(status_code=500, detail="Sentence-Transformers not available.")
	if corpus_embeddings is None or not corpus_segments:
		raise HTTPException(status_code=400, detail="Embeddings not built. Upload or set corpus first.")
	model = ensure_embed_model()
	q_vec = model.encode([query], normalize_embeddings=True)
	# cosine similarity via dot product since normalized
	sims = (q_vec @ corpus_embeddings.T)[0]
	idxs = np.argsort(sims)[::-1][:k]
	return [(int(i), float(sims[int(i)])) for i in idxs]


def min_max_scale(values: List[float]) -> List[float]:
	if not values:
		return values
	min_v = min(values)
	max_v = max(values)
	if max_v - min_v < 1e-12:
		return [0.5 for _ in values]
	return [(v - min_v) / (max_v - min_v) for v in values]


def hybrid_rank(query: str, k_lex: int, k_sem: int, alpha: float) -> List[Dict[str, Any]]:
	"""Combine BM25 and semantic scores after scaling to [0,1]."""
	lex = lexical_search(query, k=k_lex)
	sem = semantic_search(query, k=k_sem)
	# Build maps
	lex_map = {i: s for i, s in lex}
	sem_map = {i: s for i, s in sem}
	all_idxs = sorted(set(list(lex_map.keys()) + list(sem_map.keys())))
	lex_scores = [lex_map.get(i, 0.0) for i in all_idxs]
	sem_scores = [sem_map.get(i, 0.0) for i in all_idxs]
	lex_scaled = min_max_scale(lex_scores)
	sem_scaled = min_max_scale(sem_scores)
	combined: List[Tuple[int, float, float, float]] = []
	for idx, lx, sm, lx_s, sm_s in zip(all_idxs, lex_scores, sem_scores, lex_scaled, sem_scaled):
		final = alpha * lx_s + (1.0 - alpha) * sm_s
		combined.append((idx, final, lx, sm))
	# Sort by final score
	combined.sort(key=lambda x: x[1], reverse=True)
	results: List[Dict[str, Any]] = []
	for idx, final, raw_lx, raw_sm in combined:
		results.append({
			"index": idx,
			"text": corpus_segments[idx],
			"score_final": float(final),
			"score_lexical_raw": float(raw_lx),
			"score_semantic_raw": float(raw_sm),
		})
	return results


def ensure_corpus(corpus_text: str, split_mode: str = "auto"):
	"""Build or rebuild indexes from user-provided corpus text."""
	global corpus_segments, corpus_embeddings
	corpus_segments = split_into_segments(corpus_text, by=split_mode)
	if not corpus_segments:
		raise HTTPException(status_code=400, detail="Empty corpus after preprocessing.")
	# BM25
	build_bm25_index(corpus_segments)
	# Embeddings
	if SentenceTransformer is None:
		raise HTTPException(status_code=500, detail="Sentence-Transformers not available.")
	model = ensure_embed_model()
	vecs = model.encode(corpus_segments, normalize_embeddings=True, batch_size=64, convert_to_numpy=True)
	corpus_embeddings = vecs
	return {
		"num_segments": len(corpus_segments),
		"device": get_device_name(),
	}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse(
		"index.html",
		{"request": request, "title": APP_TITLE, "device": get_device_name()},
	)


@app.post("/api/check")
async def check_plagiarism(text: str = Form(...)):
	# Temporarily disabled classifier functionality
	raise HTTPException(status_code=503, detail="Classifier temporarily disabled")


@app.post("/api/hybrid_set_corpus")
async def hybrid_set_corpus(corpus: str = Form(...), split_mode: str = Form("auto")):
	"""Upload or set the reference corpus; build indices for retrieval."""
	if BM25Okapi is None:
		raise HTTPException(status_code=500, detail="rank-bm25 not installed.")
	if SentenceTransformer is None:
		raise HTTPException(status_code=500, detail="sentence-transformers not installed.")
	info = ensure_corpus(corpus, split_mode=split_mode)
	return {
		"message": "Corpus indexed successfully",
		"num_segments": info["num_segments"],
		"device": info["device"],
	}


@app.post("/api/hybrid_check")
async def hybrid_check(
	query_text: str = Form(...),
	alpha: float = Form(0.4),
	top_k_lex: int = Form(10),
	top_k_sem: int = Form(10),
	top_n: int = Form(5),
	threshold: float = Form(0.75),
):
	"""Hybrid retrieval with BM25 + Semantic embeddings and optional classifier confirmation."""
	if not corpus_segments:
		raise HTTPException(status_code=400, detail="Corpus is empty. Set corpus first.")
	query_processed = preprocess_text(query_text)
	all_ranked = hybrid_rank(query_processed, k_lex=top_k_lex, k_sem=top_k_sem, alpha=alpha)
	# Keep top-N
	results = all_ranked[:top_n]
	# Flag suspicious based on threshold
	for r in results:
		r["is_suspected"] = bool(r["score_final"] >= float(threshold))
	return {
		"query": query_processed,
		"alpha": alpha,
		"threshold": threshold,
		"results": results,
		"device": get_device_name(),
	}


if __name__ == "__main__":
	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
