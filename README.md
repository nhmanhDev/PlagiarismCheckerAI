# AI Plagiarism Checker (Hybrid Retrieval + FastAPI)

Hệ thống kiểm tra đạo văn theo hướng hybrid retrieval:
- Lexical retrieval (BM25)
- Semantic retrieval (Sentence-Transformers)
- Hybrid scoring (kết hợp cho xếp hạng cuối)
- Tùy chọn xác nhận bằng classifier: `jpwahle/longformer-base-plagiarism-detection`

## Yêu cầu

- Python 3.9+
- Các thư viện trong `requirements.txt`

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng (FastAPI + Uvicorn)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Mở trình duyệt: `http://localhost:8000/`.

## Cách sử dụng (UI)

- Mục "Thiết lập kho tham chiếu (Corpus)": dán corpus, chọn `split_mode`, bấm "Lập chỉ mục corpus".
- Mục "Kiểm tra đạo văn kiểu Hybrid": dán văn bản nghi ngờ, điều chỉnh `alpha`, `top_k_lex`, `top_k_sem`, `top_n`, `threshold`, có thể bật xác nhận classifier, sau đó chạy.
- Bảng kết quả hiển thị điểm BM25, điểm ngữ nghĩa, điểm hybrid, cờ nghi ngờ, và nhãn classifier (nếu bật).

### Giải thích các form field trong giao diện

- "Nhập một đoạn văn bản để phát hiện dấu hiệu đạo văn/diễn đạt lại bằng máy": mô tả tính năng tổng quát ở phần kiểm tra nhanh bằng classifier.
- "Thiết bị: CUDA/CPU": hiển thị thiết bị suy luận mô hình, lấy từ biến `device` trong server; nếu có GPU sẽ là CUDA, ngược lại là CPU.
- "Văn bản cần kiểm tra" + vùng nhập: dùng cho endpoint `POST /api/check` (classifier đơn), để dự đoán nhanh một đoạn văn có dấu hiệu đạo văn/paraphrase hay không.
- Nút "Kiểm tra": gửi form ở trên đến `/api/check` và hiển thị nhãn + độ tin cậy.
- Ở phần Hybrid (thêm bên dưới UI):
  - `corpus`: kho tham chiếu (nhiều đoạn), hệ thống sẽ tách câu/đoạn và lập chỉ mục BM25 + embedding.
  - `split_mode`: cách tách segment (`auto`, `sentence`, `paragraph`).
  - `query_text`: đoạn nghi ngờ cần so khớp với corpus.
  - `alpha`: trọng số kết hợp lexical/semantic trong khoảng [0,1].
  - `top_k_lex`: lấy bao nhiêu ứng viên top-k từ BM25 trước khi hợp nhất.
  - `top_k_sem`: lấy bao nhiêu ứng viên top-k từ semantic trước khi hợp nhất.
  - `top_n`: số kết quả cuối sau khi tính điểm hybrid.
  - `threshold`: ngưỡng để gắn cờ nghi ngờ (`score_final ≥ threshold`).
  - `confirm_with_classifier`: bật xác nhận bằng classifier cho từng cặp (query, candidate segment).

## API Endpoints

- `POST /api/hybrid_set_corpus`
  - form fields: `corpus` (string), `split_mode` in {`auto`,`sentence`,`paragraph`}
  - trả về: `num_segments`, `device`

- `POST /api/hybrid_check`
  - form fields: `query_text`, `alpha` (float), `top_k_lex` (int), `top_k_sem` (int), `top_n` (int), `threshold` (float), `confirm_with_classifier` (0|1)
  - trả về: danh sách `results` (kèm `score_final`, `score_lexical_raw`, `score_semantic_raw`, `is_suspected`) và `confirmations` (nếu bật)

- `POST /api/check` (classifier đơn)
  - form fields: `text`

## Ví dụ Corpus và Request mẫu

### Corpus mẫu

Bạn có thể dán corpus như sau (nhiều đoạn, mỗi đoạn cách nhau bởi xuống dòng; hệ thống vẫn sẽ tách câu theo `split_mode`):

```
Học máy là một nhánh của trí tuệ nhân tạo, tập trung vào việc cho phép máy tính học từ dữ liệu.
Các mô hình ngôn ngữ lớn có khả năng hiểu và sinh ngôn ngữ tự nhiên ở mức độ cao.
BM25 là một phương pháp xếp hạng trong truy hồi thông tin dựa trên tần suất và độ dài tài liệu.
Mã nguồn mở giúp cộng đồng phát triển nhanh hơn thông qua chia sẻ kiến thức và công cụ.
```

### Gửi corpus (cURL)

```bash
curl -X POST http://localhost:8000/api/hybrid_set_corpus \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "corpus=Học máy là một nhánh của trí tuệ nhân tạo, tập trung vào việc cho phép máy tính học từ dữ liệu.
Các mô hình ngôn ngữ lớn có khả năng hiểu và sinh ngôn ngữ tự nhiên ở mức độ cao.
BM25 là một phương pháp xếp hạng trong truy hồi thông tin dựa trên tần suất và độ dài tài liệu.
Mã nguồn mở giúp cộng đồng phát triển nhanh hơn thông qua chia sẻ kiến thức và công cụ." \
  --data-urlencode "split_mode=auto"
```

Phản hồi ví dụ:

```json
{
  "message": "Corpus indexed successfully",
  "num_segments": 6,
  "device": "CUDA"
}
```

### Kiểm tra Hybrid (cURL)

```bash
curl -X POST http://localhost:8000/api/hybrid_check \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "query_text=Một phương pháp xếp hạng phổ biến trong truy hồi thông tin là BM25." \
  --data-urlencode "alpha=0.4" \
  --data-urlencode "top_k_lex=10" \
  --data-urlencode "top_k_sem=10" \
  --data-urlencode "top_n=5" \
  --data-urlencode "threshold=0.75" \
  --data-urlencode "confirm_with_classifier=1"
```

Phản hồi sẽ bao gồm `results` (các segment phù hợp nhất) và `confirmations` (nếu bật), ví dụ:

```json
{
  "query": "mot phuong phap xep hang pho bien trong truy hoi thong tin la bm25.",
  "alpha": 0.4,
  "threshold": 0.75,
  "results": [
    {
      "index": 2,
      "text": "bm25 la mot phuong phap xep hang trong truy hoi thong tin dua tren tan suat va do dai tai lieu.",
      "score_final": 0.89,
      "score_lexical_raw": 5.23,
      "score_semantic_raw": 0.74,
      "is_suspected": true
    }
  ],
  "confirmations": [
    { "index": 2, "label": "PLAGIARISM", "score": 0.87 }
  ],
  "device": "CUDA"
}
```

### Classifier đơn (cURL)

```bash
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "text=Câu này dùng để kiểm tra nhanh dấu hiệu đạo văn bằng classifier."
```

## Ghi chú về mô hình

- Mô hình được huấn luyện để phát hiện văn bản bị diễn đạt lại nhằm che giấu hành vi đạo văn.
- Kết quả chỉ mang tính tham khảo, cần kết hợp với đánh giá thủ công và các công cụ khác.
- Đầu vào quá dài có thể bị cắt tùy mô hình. Với hybrid, văn bản được tách thành các segment để so khớp.

## Docker

### Build
```bash
docker build -t plagiarism-checker:latest .
```

### Run (CPU)
```bash
docker run --rm -p 8000:8000 plagiarism-checker:latest
```

### Run (GPU, nếu có NVIDIA Container Toolkit)
```bash
docker run --rm --gpus all -p 8000:8000 plagiarism-checker:latest
```

Mở `http://localhost:8000/`.

## Bảo mật & Quyền riêng tư

- Ứng dụng tải mô hình từ Hugging Face lần đầu; suy luận diễn ra cục bộ sau khi tải.
- Không lưu trữ văn bản người dùng. Corpus và embedding được giữ trong bộ nhớ; restart sẽ xóa.

## Tham khảo

- Longformer classifier: `jpwahle/longformer-base-plagiarism-detection`
- Sentence embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- BM25: `rank-bm25`
