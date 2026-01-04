# Hệ Thống Kiểm Tra Đạo Văn AI

Sistema plagiarism detection cho văn bản tiếng Việt với **Multi-Stage Retrieval** (BM25 + Semantic Embeddings + Cross-Encoder Re-ranking).

## 🎯 Research Foundation

**Method:** Multi-Stage Information Retrieval adapted for Plagiarism Detection  
**Pipeline:** BM25 Lexical → Dense Semantic → Cross-Encoder Re-ranking  
**Application:** Text similarity với threshold-based classification

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- 8GB RAM minimum

### Option 1: Run Locally

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python run.py
# → http://localhost:8000

# 2. Frontend (terminal mới)
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Option 2: Docker (Recommended)

```bash
docker-compose up -d
# → Frontend: http://localhost:3000
# → Backend API: http://localhost:8000
# → API Docs: http://localhost:8000/docs
```

## 📝 Usage Examples

### Example 1: Tạo Kho Tài Liệu

**Via Web UI:**
1. Mở http://localhost:3000
2. Click "Quản Lý Kho Tài Liệu"
3 Click "+ Tạo Kho Mới"
4. Nhập:
   - Tên: "Tài liệu AI"
   - Nội dung: ```
   Học máy là một tập con của trí tuệ nhân tạo, tập trung vào việc xây dựng các hệ thống có khả năng học từ dữ liệu.
   
   Python là ngôn ngữ lập trình phổ biến cho học máy do có nhiều thư viện mạnh mẽ như TensorFlow, PyTorch.
   
   Mạng nơ-ron sâu (Deep Learning) là một nhánh của học máy sử dụng mạng nơ-ron nhiều lớp để học các biểu diễn phức tạp.
   ```
5. Click "Tạo Kho Tài Liệu"
6. Click "Kích Hoạt" trên kho vừa tạo

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/corpus \
  -F "name=Tài liệu AI" \
  -F "corpus_text=Học máy là một tập con của trí tuệ nhân tạo..."
```

### Example 2: Kiểm Tra Đạo Văn

**Via Web UI:**
1. Click "Kiểm Tra Đạo Văn"
2. Nhập văn bản cần kiểm tra:
   ```
   Machine learning là một phần của AI, tập trung việc xây dựng hệ thống học từ data.
   ```
3. Click "Kiểm Tra Đạo Văn"
4. Xem kết quả với điểm similarity

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/plagiarism/check-multistage \
  -F "query_text=Machine learning là một phần của AI" \
  -F "use_reranker=true" \
  -F "top_n=5"
```

**Response Example:**
```json
{
  "query": "Machine learning là một phần của AI",
  "results": [
    {
      "text": "Học máy là một tập con của trí tuệ nhân tạo...",
      "score_final": 0.92,
      "score_lexical_raw": 0.88,
      "score_semantic_raw": 0.94,
      "score_reranker": 0.95,
      "is_suspected": true
    }
  ],
  "method": "multi-stage",
  "reranker_used": true,
  "threshold": 0.75
}
```

### Example 3: Test với Various Queries

**High Similarity (>0.9):** Paraphrase/Translation
```
Query: "Deep learning sử dụng neural networks nhiều tầng"
Match: "Mạng nơ-ron sâu sử dụng mạng nơ-ron nhiều lớp"
Score: 0.94 → PLAGIARISM DETECTED
```

**Medium Similarity (0.6-0.9):** Related content
```
Query: "Python có nhiều thư viện ML"
Match: "Python là ngôn ngữ phổ biến có TensorFlow, PyTorch"
Score: 0.78 → SUSPECTED
```

**Low Similarity (<0.6):** Different topic
```
Query: "React is a JavaScript library"
Match: "Học máy là một tập con của AI"
Score: 0.15 → NOT PLAGIARISM
```

## 🏗️ Architecture

**3-Stage Pipeline:**
```
Input Query
    ↓
[Stage 1] BM25 Retrieval (Lexical)
    ↓ top-100 candidates
[Stage 2] Dense Retrieval (Semantic)
    ↓ top-20 candidates  
[Stage 3] Cross-Encoder Re-ranking
    ↓ top-5 results
Final Results (with scores 0-1)
```

**Tech Stack:**
- **Backend:** FastAPI + BM25Okapi + SentenceTransformers
- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **Models:** paraphrase-multilingual-MiniLM-L12-v2, ms-marco-MiniLM
- **Storage:** JSON files (corpus metadata & segments)

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/              # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── schemas/             # Pydantic models
│   │   └── core/                # Config
│   ├── data/                    # Corpus storage (created at runtime)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               # React pages
│   │   ├── components/          # UI components
│   │   └── services/            # API clients
│   ├── Dockerfile
│   ├── nginx.conf               # Nginx config
│   └── package.json
├── research/                    # Research scripts & experiments
├── docs/                        # Documentation
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

Edit `backend/app/core/config.py`:
```python
CORPUS_STORAGE_DIR = Path("../data/corpora")
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_ALPHA = 0.4        # BM25 vs Semantic weight
DEFAULT_THRESHOLD = 0.75   # Plagiarism threshold
DEFAULT_TOP_N = 5          # Number of results
```

## 📊 Performance

- **Response Time:** <200ms (cached corpus)
- **Precision@5:** ~85%
- **F1-Score:** ~88%
- **Languages:** Vietnamese (optimized), Multilingual support

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Frontend build fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Docker errors:**
```bash
# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

**CORS errors:**
- Check backend CORS settings in `config.py`
- Verify frontend API URL in `.env`

## 📚 Documentation

- **[WIKI](WIKI.md)** - Detailed technical documentation
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation
- **[Research](/research)** - Implementation details & experiments

## 🔬 Research

**Core Method:**
- Multi-stage information retrieval (BM25 + Dense + Re-ranking)
- Adapted from Vietnamese legal document retrieval (2024-2025)
- Application: Plagiarism detection = Text similarity + threshold classification

**Models Used:**
- Lexical: BM25Okapi
- Semantic: paraphrase-multilingual-MiniLM-L12-v2
- Re-ranker: cross-encoder/ms-marco-MiniLM-L-6-v2
- Vietnamese NLP: underthesea (word segmentation)

## 📄 License

MIT

## 👥 Contributing

Contributions welcome! Please read contributing guidelines first.

---

**Quick Links:**
- 🌐 [Frontend](http://localhost:3000)
- 🔌 [API](http://localhost:8000)
- 📖 [API Docs](http://localhost:8000/docs)
- 📝 [WIKI](WIKI.md)
