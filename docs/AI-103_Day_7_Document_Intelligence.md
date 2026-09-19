# AI-103 — Day 7: Azure AI Document Intelligence (Chi tiết từng bước từ Prebuilt đến Custom Model Training)

> **Mục tiêu:** Làm chủ toàn diện dịch vụ **Azure AI Document Intelligence** (Form Recognizer) theo chuẩn đề thi AI-103: từ phân tích bóc tách bảng biểu/checkbox bằng **Layout API**, sử dụng **Prebuilt Models**, đến **quy trình huấn luyện mô hình tùy biến (Custom Template & Custom Neural)** bằng `DocumentModelAdministrationClient`, và ghép nối mô hình (**Composed Models**).

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** **$0.00** (Dùng gói Free Tier `F0`: 500 trang/tháng miễn phí) hoặc **<$0.20** với `S0`.  
**Phạm vi lab:** `rg-ai103-lab` → Azure AI Document Intelligence (`F0` hoặc Multi-service Cognitive Services).

---

## 1. Mental Model: Phân cấp Năng lực Document Intelligence

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      AZURE AI DOCUMENT INTELLIGENCE CAPABILITIES                        │
│                                                                                         │
│  ┌───────────────────────┐   ┌────────────────────────┐   ┌──────────────────────────┐  │
│  │ 1. Document Analysis  │   │ 2. Prebuilt Models     │   │ 3. Custom Models         │  │
│  │    (Chung cho mọi doc)│   │    (Loại tài liệu mẫu) │   │    (Doanh nghiệp tự train)│  │
│  ├───────────────────────┤   ├────────────────────────┤   ├──────────────────────────┤  │
│  │ • prebuilt-read (OCR) │   │ • prebuilt-invoice     │   │ • Custom Template Model  │  │
│  │ • prebuilt-layout     │   │ • prebuilt-receipt     │   │   (Layout cố định, 5 mẫu)│  │
│  │   - Tables (bảng)     │   │ • prebuilt-idDocument  │   │ • Custom Neural Model    │  │
│  │   - Selection marks   │   │ • prebuilt-tax.us.w2   │   │   (Văn bản biến thiên)   │  │
│  │   - Markdown export   │   │ • prebuilt-contract    │   │ • Composed Model         │  │
│  │   - Reading order     │   │ • prebuilt-healthCard  │   │   (Gộp tối đa 200 models)│  │
│  └───────────────────────┘   └────────────────────────┘   └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Hướng dẫn Từng bước: Phân tích Cấu trúc phức tạp bằng Layout API (Step-by-Step)

Mô hình `prebuilt-layout` là trọng tâm của AI-103 vì đây là bước tiền xử lý bắt buộc trước khi đưa tài liệu vào hệ thống RAG hoặc LLM.

### Bước 1: Khởi tạo Client và Gửi Yêu cầu Phân tích

Cài đặt SDK:
```bash
uv add azure-ai-documentintelligence
```

Mã nguồn Python phân tích Layout xuất định dạng Markdown và trích xuất Bảng biểu:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    AnalyzeResult,
    DocumentAnalysisFeature
)

ENDPOINT = "https://<your-di-service>.cognitiveservices.azure.com/"
KEY = "<your-key>"

client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

# File PDF mẫu chứa bảng biểu và checkbox
sample_pdf_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

# Gửi yêu cầu phân tích bất đồng bộ (Poller pattern)
poller = client.begin_analyze_document(
    model_id="prebuilt-layout",
    analyze_request=AnalyzeDocumentRequest(url_source=sample_pdf_url),
    output_content_format="markdown",                      # Xuất định dạng Markdown cho RAG
    features=[DocumentAnalysisFeature.STYLE_INFO]          # Nhận diện font chữ, chữ viết tay
)

result: AnalyzeResult = poller.result()
```

---

### Bước 2: Bóc tách Bảng biểu chi tiết (Tables, Rows, Columns & Spanning)

Đề thi AI-103 thường yêu cầu duyệt qua từng ô trong bảng (cells), xác định hàng, cột và xử lý ô gộp (row_span, column_span):

```python
if result.tables:
    print(f"Tổng số bảng biểu phát hiện: {len(result.tables)}\n")
    
    for table_idx, table in enumerate(result.tables, 1):
        print(f"--- BẢNG {table_idx} (Kích thước: {table.row_count} hàng x {table.column_count} cột) ---")
        
        # Tạo ma trận lưới để hiển thị
        grid = [["" for _ in range(table.column_count)] for _ in range(table.row_count)]
        
        for cell in table.cells:
            # cell.row_index, cell.column_index: Tọa độ ô
            # cell.content: Nội dung văn bản trong ô
            row = cell.row_index
            col = cell.column_index
            grid[row][col] = cell.content
            
            # Kiểm tra ô gộp (Bẫy đề thi)
            if (cell.row_span and cell.row_span > 1) or (cell.column_span and cell.column_span > 1):
                print(f" Ô gộp tại [{row}, {col}]: span ({cell.row_span} hàng, {cell.column_span} cột)")

        for row_data in grid:
            print(" | ".join(row_data))
        print("\n")
```

---

### Bước 3: Nhận diện Checkbox / Radio Button (Selection Marks)

Trong các tờ khai đăng ký hoặc khảo sát:

```python
if result.pages:
    for page in result.pages:
        print(f"Trang {page.page_number} có {len(page.selection_marks or [])} ô đánh dấu:")
        for mark in page.selection_marks or []:
            # mark.state có thể là 'selected' (đã tích) hoặc 'unselected' (chưa tích)
            status = "ĐÃ CHỌN [X]" if mark.state == "selected" else "CHƯA CHỌN [ ]"
            # mark.polygon: Tọa độ 4 góc của checkbox trên mặt giấy
            print(f" - Trạng thái: {status} (Độ tự tin: {mark.confidence * 100:.1f}%)")
```

---

## 3. Hướng dẫn Từng bước: Huấn luyện Custom Model (Custom Template vs Neural)

Khi doanh nghiệp có mẫu biểu riêng (ví dụ: Đơn xin cấp phát thiết bị nội bộ), ta dùng `DocumentModelAdministrationClient` để train model:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CUSTOM MODEL TRAINING LIFECYCLE                        │
│                                                                             │
│  [5+ Sample Documents]                                                      │
│           │                                                                 │
│           ▼                                                                 │
│  [Azure Blob Container] ◄─── Document Intelligence Studio (Labeling / OCR)  │
│  (Chứa file PDF + .labels.json + .ocr.json)                                │
│           │                                                                 │
│           ▼                                                                 │
│  DocumentModelAdministrationClient.begin_build_document_model()             │
│           ├── build_mode = DocumentBuildMode.TEMPLATE  (Form cố định)       │
│           └── build_mode = DocumentBuildMode.NEURAL    (Văn bản biến thiên) │
│           │                                                                 │
│           ▼                                                                 │
│  [Custom Trained Model: 'my-custom-tax-model']                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Bước 1: Chuẩn bị Dữ liệu Huấn luyện trong Blob Storage
1. Tạo một Azure Storage Container (ví dụ `di-training-data`).
2. Tải lên tối thiểu **5 tài liệu mẫu**.
3. Dùng **Document Intelligence Studio** để gán nhãn (Labeling) các trường cần trích xuất (ví dụ: `EmployeeName`, `DeviceType`, `RequestDate`).
4. Studio sẽ tự động sinh các file `.labels.json` và `.ocr.json` lưu thẳng vào container.
5. Cấp quyền Managed Identity hoặc sinh SAS URL trỏ tới container này.

---

### Bước 2: Viết mã Python Huấn luyện Model

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentModelAdministrationClient
from azure.ai.documentintelligence.models import (
    BuildDocumentModelRequest,
    DocumentBuildMode,
    AzureBlobContentSource
)

ADMIN_ENDPOINT = "https://<your-di-service>.cognitiveservices.azure.com/"
ADMIN_KEY = "<your-key>"
BLOB_CONTAINER_SAS_URL = "https://<storage>.blob.core.windows.net/di-training-data?<SAS-TOKEN>"

admin_client = DocumentModelAdministrationClient(
    endpoint=ADMIN_ENDPOINT,
    credential=AzureKeyCredential(ADMIN_KEY)
)

# Khởi tạo job huấn luyện Custom Neural Model
poller = admin_client.begin_build_document_model(
    BuildDocumentModelRequest(
        model_id="company-equipment-form-v1",
        description="Mô hình trích xuất đơn cấp phát thiết bị của công ty",
        build_mode=DocumentBuildMode.NEURAL,  # hoặc DocumentBuildMode.TEMPLATE
        azure_blob_source=AzureBlobContentSource(container_url=BLOB_CONTAINER_SAS_URL)
    )
)

model_info = poller.result()

print(f" Huấn luyện thành công Model ID: {model_info.model_id}")
print(f"Phiên bản API tạo: {model_info.api_version}")
print(f"Các trường dữ liệu đã học:")
for field_name, field_def in model_info.doc_types["company-equipment-form-v1"].fields.items():
    print(f" - {field_name} (Kiểu dữ liệu: {field_def.type})")
```

---

### Bước 3: Ghép nối Mô hình (Composed Models)

Khi ứng dụng cần xử lý nhiều mẫu đơn khác nhau (ví dụ: Form nghỉ phép, Form công tác, Form hoàn ứng) mà client chỉ muốn gọi 1 API duy nhất:

```python
from azure.ai.documentintelligence.models import ComposeDocumentModelRequest

# Ghép 3 model con vào 1 model tổng
compose_poller = admin_client.begin_compose_document_model(
    ComposeDocumentModelRequest(
        model_id="company-all-forms-composed",
        description="Mô hình tổng hợp tự động định tuyến các biểu mẫu nội bộ",
        component_model_ids=[
            "company-equipment-form-v1",
            "company-leave-request-v2",
            "company-expense-report-v1"
        ]
    )
)

composed_model = compose_poller.result()
print(f" Đã tạo Composed Model thành công: {composed_model.model_id}")
```

> [!NOTE]
> **Điểm thi AI-103:** Một Composed Model có thể kết hợp tối đa **100 mô hình con (hoặc 200 mô hình tùy gói)**. Khi gửi tài liệu vào Composed Model, Document Intelligence sẽ tự động phân loại xem tài liệu khớp với model con nào và trích xuất đúng schema đó.

---

## 4. Hướng dẫn Thao tác trên Document Intelligence Studio UI (No-code)

Trong đề thi và công việc thực tế, giao diện **Azure AI Document Intelligence Studio** ([documentintelligence.ai.azure.com](https://documentintelligence.ai.azure.com)) là công cụ trực quan hóa mạnh mẽ nhất để thử nghiệm và gán nhãn dữ liệu:

### 4.1 Thử nghiệm Trực quan Layout & Prebuilt Models
1. Truy cập [Document Intelligence Studio](https://documentintelligence.ai.azure.com), đăng nhập tài khoản Azure và chọn resource trong `rg-ai103-lab`.
2. **Kiểm thử Layout:**
   - Bấm vào thẻ **Layout**.
   - Bấm nút **Analyze** trên tài liệu mặc định hoặc upload file PDF của bạn.
   - Tại cột bên phải, chuyển đổi giữa các tab:
     - *Result:* Xem tài liệu trực quan với các khung viền màu bao quanh văn bản.
     - *Markdown:* Xem tài liệu đã được chuyển đổi sang chuẩn Markdown (bảng biểu được định dạng bằng cú pháp `|---|`).
     - *JSON:* Xem cấu trúc cây dữ liệu thô trả về từ API.
   - Tại thanh công cụ dưới trang tài liệu, bật/tắt các lớp **Layers**: `Text lines`, `Words`, `Tables`, `Selection marks` để quan sát cách AI nhận diện từng thành phần.
3. **Kiểm thử Prebuilt Invoices/Receipts:**
   - Quay lại trang chủ Studio, chọn thẻ **Invoices**.
   - Upload hóa đơn mẫu: Cột bên phải sẽ tự động hiển thị danh sách các cặp **Field - Value** (ví dụ: `VendorName`, `InvoiceDate`, `InvoiceTotal`, `LineItems`) kèm theo điểm tin cậy (**Confidence Score**, ví dụ: `0.98`).

---

### 4.2 Quy trình Huấn luyện Custom Model trên Studio UI (Click-by-click)

Đây là quy trình bắt buộc phải nắm vững khi gặp các câu hỏi thực hành cấu hình trong kỳ thi AI-103:

```text
[Create Project] ──► [Connect Storage] ──► [Label 5+ Docs] ──► [Train Model] ──► [Test & Compose]
```

1. **Bước 1 — Tạo Project:**
   - Tại trang chủ Studio, chọn thẻ **Custom extraction model** $\rightarrow$ Bấm nút **Create a project**.
   - Nhập tên dự án (ví dụ: `company-form-project`).
2. **Bước 2 — Kết nối Dữ liệu Azure:**
   - Chọn Subscription, Resource Group `rg-ai103-lab`, và Document Intelligence Service.
   - Chọn Storage account và Blob Container chứa 5+ file tài liệu mẫu đã chuẩn bị.
   - Bấm **Create project**.
3. **Bước 3 — Gán nhãn (Labeling UI):**
   - Tại cột bên phải (**Fields**), bấm **+ Add field**:
     - Chọn kiểu dữ liệu: `Field Text`, `Field Number`, `Field Date`, hoặc `Selection Mark`.
     - Đặt tên trường (ví dụ: `EmployeeName`, `TotalCost`, `ApprovedCheckbox`).
   - Chọn một tài liệu trong danh sách bên trái $\rightarrow$ dùng chuột bôi đen vùng văn bản trên file PDF $\rightarrow$ bấm vào tên trường tương ứng để gán giá trị.
   - Lặp lại việc gán nhãn cho **tối thiểu 5 tài liệu mẫu** (tất cả tài liệu phải có trạng thái *Labeled* màu xanh).
4. **Bước 4 — Huấn luyện Model (Training):**
   - Bấm nút **Train** ở thanh công cụ góc trên bên phải.
   - Nhập **Model ID** (ví dụ: `equipment-model-v1`).
   - Chọn **Build Mode** (Bẫy đề thi):
     - Chọn `Template`: Nếu các tài liệu có bố cục tọa độ pixel cố định 100%.
     - Chọn `Neural`: Nếu tài liệu có bố cục co giãn, số dòng thay đổi linh hoạt.
   - Bấm **Train** và chờ tiến trình hoàn tất trong 1–3 phút.
5. **Bước 5 — Kiểm thử (Testing) & Ghép Model (Compose):**
   - Bấm tab **Test** ở menu trên cùng $\rightarrow$ upload một file tài liệu mới $\rightarrow$ bấm **Analyze** để đối chiếu các trường trích xuất tự động.
   - **Ghép Model (Compose):** Vào tab **Models** $\rightarrow$ tích chọn nhiều custom models khác nhau $\rightarrow$ bấm nút **Compose** trên thanh công cụ $\rightarrow$ nhập `ComposedModelId` để gom thành một endpoint duy nhất.

---

## 5. Kiến thức thi trọng tâm (Exam Objectives & Traps)

| Tình huống trong đề thi | Giải pháp / Lựa chọn chính xác |
| :--- | :--- |
| Cần trích xuất hóa đơn thanh toán của các khách sạn trên toàn cầu | Sử dụng **`prebuilt-receipt`** hoặc **`prebuilt-invoice`**. Không cần tự gán nhãn hay train custom model. |
| Tài liệu có các ô checkbox đánh dấu giới tính hoặc đồng ý điều khoản | Sử dụng **Layout API** (`prebuilt-layout`), kiểm tra danh sách `selection_marks` và trường `state eq 'selected'`. |
| Cần số lượng tài liệu tối thiểu để bắt đầu huấn luyện một Custom Model | **5 tài liệu mẫu** (Minimum 5 documents). |
| Công ty có mẫu hợp đồng lao động 10 trang, bố cục từng trang có thể co giãn dòng tùy thuộc người ký | Chọn **Custom Neural Model** (học ngữ nghĩa và ngôn ngữ, không bị trượt khi dòng xê dịch). |
| Biểu mẫu scan là tờ khai hải quan có ô kẻ khung cố định 100% tọa độ pixel | Chọn **Custom Template Model** (khớp theo visual layout và tọa độ hình học cố định). |
| Muốn xuất tài liệu PDF sang dạng Markdown để giữ cấu trúc bảng biểu nạp vào Azure AI Search | Dùng Layout API với tùy chọn **`output_content_format="markdown"`**. |

---

## 5. Definition of Done — Day 7

- [ ] Phân biệt được sự khác nhau giữa `prebuilt-read` (OCR thuần) và `prebuilt-layout` (Tables, Checkboxes, Markdown).
- [ ] Viết được code bóc tách ma trận bảng biểu (`row_count`, `column_count`, `cells`, `row_span`).
- [ ] Nêu rõ quy trình huấn luyện Custom Model bằng `DocumentModelAdministrationClient` với dữ liệu trong Azure Blob Storage.
- [ ] Phân biệt chính xác khi nào dùng Custom Template (tọa độ cứng) vs Custom Neural (ngữ nghĩa linh hoạt).
- [ ] Giải thích được nguyên lý hoạt động của Composed Model (ghép nhiều model con).

---

## Sources (Official, checked 16/09/2026)

- [Azure AI Document Intelligence overview](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview)
- [Document Intelligence Layout model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-layout)
- [How to build a custom model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/build-a-custom-model)
- [Compose custom models](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/compose-custom-models)
