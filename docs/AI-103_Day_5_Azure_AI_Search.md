# AI-103 — Day 5: Azure AI Search

> **Mục tiêu:** Nắm vững nền tảng cốt lõi của kỹ thuật RAG trong Azure: kiến trúc **Search Service, Index, Indexer, Skillset**, sự khác biệt giữa **Keyword (BM25), Vector, Hybrid Search (RRF)** và **Semantic Ranker**.

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** **$0.00** (nếu dùng Free Tier `F1`) hoặc $0.20–$**0.50** (nếu tạo Basic Tier để thử nghiệm rồi **XÓA NGAY trong vòng 1–2 giờ**).  
**Phạm vi lab:** `rg-ai103-lab` → Azure AI Search Service.

---

## 1. Vị trí của Azure AI Search trong đề thi AI-103

Azure AI Search là dịch vụ xuất hiện nhiều nhất trong nhóm câu hỏi về **Information Retrieval** và **RAG/Knowledge Base**:

1. Thiết kế Schema Index (chọn đúng thuộc tính trường: `searchable`, `filterable`, `facetable`, `sortable`, `retrievable`).
2. Kiến trúc ETL/Data Ingestion: Data Source → Indexer → Skillset → Index.
3. Kỹ thuật tìm kiếm: So sánh độ chính xác và chi phí giữa **Keyword**, **Vector**, **Hybrid Search (RRF)**, và **Semantic Ranker**.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA INGESTION (ETL)                            │
│                                                                             │
│  ┌─────────────┐       ┌─────────────┐       ┌────────────┐       ┌───────┐ │
│  │ Data Source │ ────> │   Indexer   │ ────> │  Skillset  │ ────> │ Index │ │
│  │ (Blob/SQL)  │       │  (Cracking) │       │ (AI/Vector)│       │       │ │
│  └─────────────┘       └─────────────┘       └────────────┘       └───┬───┘ │
└───────────────────────────────────────────────────────────────────────┼─────┘
                                                                        │
┌───────────────────────────────────────────────────────────────────────┼─────┐
│                            QUERY EXECUTION                            ▼     │
│                                                                             │
│     [User Query] ──> Hybrid Query (BM25 + Vector HNSW)                      │
│                                  │                                          │
│                                  ▼                                          │
│                    [Reciprocal Rank Fusion (RRF)]                           │
│                                  │ (Top 50 kết quả kết hợp)                 │
│                                  ▼                                          │
│                    [Semantic Ranker (L2 Re-ranking)]                        │
│                                  │ (Mô hình ngôn ngữ Turing đọc hiểu)        │
│                                  ▼                                          │
│               [Top Results + Semantic Captions + Answers]                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Các thành phần kiến trúc cốt lõi

### 2.1 Indexer vs Skillset vs Data Source


| Thành phần       | Vai trò thực tế                                                                                                                                                                                                      | Lưu ý đề thi                                                                                         |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| **Data Source**  | Định nghĩa kết nối tới dữ liệu nguồn (Azure Blob, Azure SQL, Cosmos DB, ADLS Gen2).                                                                                                                                  | Hỗ trợ Change Detection (High Watermark Policy hoặc SQL Integrated Change Tracking).                 |
| **Indexer**      | Bộ thu thập dữ liệu (Crawler/ETL). Chịu trách nhiệm bóc tách văn bản thô từ file (PDF, DOCX, XLSX) gọi là **Document Cracking**.                                                                                     | Chạy theo lịch trình (schedule) hoặc trigger thủ công. Không lưu dữ liệu tìm kiếm.                   |
| **Skillset**     | Chuỗi các AI enrichment tasks được nhúng trong quá trình Indexer chạy: OCR đọc ảnh, trích xuất thực thể (Entity Recognition), dịch ngôn ngữ, chunking (Text Split Skill), và gọi Azure OpenAI tạo Vector Embeddings. | Lưu ý: Các skill này có thể dùng Azure AI Services gắn kèm (có thể phát sinh chi phí theo lượt gọi). |
| **Search Index** | Kho dữ liệu có cấu trúc chứa các trường văn bản và vector embeddings đã được đánh chỉ mục để phục vụ truy vấn tìm kiếm tốc độ cao.                                                                                   | Đây là nơi thực tế lưu trữ dữ liệu và xử lý truy vấn của người dùng.                                 |


---

### 2.2 Thuộc tính các trường trong Index (Index Field Attributes)

Đây là dạng câu hỏi "bẫy" cực kỳ phổ biến trong đề thi AI-103:


| Thuộc tính        | Ý nghĩa                                                                                                                                          | Ví dụ áp dụng                                                                       |
| :----------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------- |
| `**searchable**`  | Văn bản được tokenize qua analyzer để tìm kiếm toàn văn (Full-text / BM25). Chỉ áp dụng cho kiểu chuỗi (`Edm.String`, `Collection(Edm.String)`). | Nội dung tài liệu, tiêu đề bài viết.                                                |
| `**filterable**`  | Cho phép lọc chính xác bằng cú pháp OData (`$filter=category eq 'Finance'`).                                                                     | Phân loại phòng ban, trạng thái, ngày tháng.                                        |
| `**sortable**`    | Cho phép sắp xếp thứ tự kết quả (`$orderby=publishedDate desc`).                                                                                 | Ngày phát hành, giá tiền, số điểm.                                                  |
| `**facetable**`   | Cho phép đếm số lượng kết quả theo danh mục để hiển thị UI lọc đa diện (Faceted navigation).                                                     | Nhãn danh mục, tác giả, tag.                                                        |
| `**retrievable**` | Cho phép trường này xuất hiện trong JSON trả về cho client. Nếu bỏ chọn, trường vẫn tìm được nhưng không lấy ra đọc được.                        | Các trường nhạy cảm, hoặc vector embeddings (không cần lấy lại 1536 float numbers). |


---

## 3. Các chế độ tìm kiếm: Từ BM25 đến Semantic Ranker

### A. Keyword Search (BM25)

- Dùng giải thuật **BM25** (Best Matching 25) so khớp tần suất từ ngữ (TF-IDF cải tiến).
- **Ưu điểm:** Cực nhanh, chính xác với từ khóa đặc thù (mã SKU, tên riêng, mã lỗi kỹ thuật `ERR_404`).
- **Nhược điểm:** Không hiểu ngữ nghĩa, từ đồng nghĩa (tìm "ô tô" không ra "xe hơi").

### B. Vector Search

- Biến đổi câu hỏi và tài liệu thành vector số thực đa chiều (ví dụ: model `text-embedding-3-small` sinh 1536 chiều).
- Dùng thuật toán khoảng cách: **Cosine Similarity**, **Euclidean**, hoặc **Dot Product** với cấu trúc đồ thị **HNSW** (Hierarchical Navigable Small World) hoặc Exhaustive KNN.
- **Ưu điểm:** Hiểu ngữ nghĩa sâu sắc, đa ngôn ngữ, không phụ thuộc chính xác từng con chữ.
- **Nhược điểm:** Kém hơn với mã lỗi, tên mã viết tắt hoặc từ khóa chuyên ngành hiếm gặp.

### C. Hybrid Search (Keyword + Vector với RRF)

- Gửi đồng thời truy vấn BM25 và truy vấn Vector vào Index.
- Kết hợp 2 tập kết quả lại bằng thuật toán **Reciprocal Rank Fusion (RRF)**.
- **Đề thi:** Luôn là lựa chọn **khuyến nghị hàng đầu (Best Practice)** cho hệ thống RAG hiện đại để dung hòa ưu điểm của cả hai.

### D. Semantic Ranker (L2 Deep Re-ranking)

- Là một mô hình học sâu (dựa trên Turing model của Microsoft) chạy ở bước thứ 2 (L2) sau khi Hybrid search đã lấy ra top 50 kết quả.
- Đọc hiểu lại toàn bộ đoạn văn cảnh để chấm lại điểm phù hợp (`@search.rerankerScore`).
- Trích xuất trực tiếp **Semantic Captions** (đoạn trích nổi bật) và **Semantic Answers** (câu trả lời trực tiếp cho câu hỏi).

---

## 4. Bảng phân cấp Chi phí &amp; Sizing (Cực kỳ quan trọng để giữ Budget)


| Tier                | Giá tham khảo                 | Vector Search                    | Semantic Ranker                  | Gợi ý cho Lab AI-103                                                                                  |
| :------------------- | :----------------------------- | :-------------------------------- | :-------------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Free (`F1`)**     | **$0 / tháng**                | Hỗ trợ (tối đa 50MB, 3 indexes)  | **Không hỗ trợ**                 | **Dùng chính cho bài học:** Học schema, field attributes, indexer, test vector search nhỏ.            |
| **Basic**           | ~~$75 / tháng (~~$0.10 / giờ) | Hỗ trợ (2GB storage, 15 indexes) | Hỗ trợ (tính thêm phí per query) | Chỉ tạo nếu muốn test tính năng Semantic Ranker, sau đó **XÓA NGAY trong vòng 60 phút** (tốn ~$0.10). |
| **Standard (`S1`)** | ~$250 / tháng                 | Production scale                 | Hỗ trợ cao                       | **Tránh xa:** Quá đắt, không dùng cho cá nhân học tập.                                                |


> [!WARNING]
> Azure AI Search **không có nút Stop/Pause**. Khi bạn tạo một Search Service (kể cả Basic), Azure sẽ tính tiền theo từng giờ tồn tại của resource bất kể bạn có truy vấn hay không.
> **Nguyên tắc an toàn:** Dùng tier **Free (F1)** trước. Nếu cần test Semantic Ranker ở Basic, phải đặt hẹn giờ báo thức để xóa resource ngay sau khi làm lab xong!

---

## 5. Definition of Done — Day 5

- [x] Nêu đúng luồng dữ liệu: Data Source → Indexer → Skillset → Index.
- [x] Phân biệt chính xác các thuộc tính trường: `searchable`, `filterable`, `sortable`, `facetable`, `retrievable`.
- [x] Giải thích được sự khác nhau và cách thức hoạt động của Hybrid Search kết hợp thuật toán RRF.
- [x] Hiểu rõ vai trò của Semantic Ranker trong việc trích xuất Semantic Captions và Answers.
- [x] Nắm vững quy tắc chi phí: Dùng Free Tier F1 để tiết kiệm budget, tuyệt đối không để quên resource Basic/Standard qua đêm.

---

## Sources (Official, checked 16/09/2026)

- [Azure AI Search service pricing](https://azure.microsoft.com/en-us/pricing/details/search/)
- [Skillset concepts in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/cognitive-search-concept-intro)
- [Hybrid search using Reciprocal Rank Fusion (RRF)](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
- [Semantic ranking in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)

