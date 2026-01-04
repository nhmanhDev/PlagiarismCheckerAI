# Backend Application Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── __init__.py
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── corpus.py   # Corpus endpoints
│   │           ├── plagiarism.py # Check endpoints
│   │           └── system.py   # Status endpoints
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── plagiarism_service.py
│   │   ├── corpus_service.py
│   │   ├── document_service.py
│   │   ├── vietnamese_service.py
│   │   └── reranker_service.py
│   │
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration
│   │   └── dependencies.py     # Shared dependencies
│   │
│   └── schemas/                # Pydantic schemas
│       ├── __init__.py
│       ├── corpus.py
│       ├── plagiarism.py
│       └── response.py
│
├── requirements.txt
├── Dockerfile
└── README.md
```

## Files to Move

From root → backend/app/services/:
- vietnamese_processor.py → vietnamese_service.py
- pdf_processor.py → document_service.py
- corpus_manager.py → (integrate into corpus_service.py)
- reranker.py → reranker_service.py

Keep in root (for research/dev):
- research_implementation.py
- research_extensions.py
- benchmark_loader.py
- experiments.py
- test_modules.py
