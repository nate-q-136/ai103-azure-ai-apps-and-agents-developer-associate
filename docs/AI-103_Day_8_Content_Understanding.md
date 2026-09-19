# AI-103 — Day 8: Azure AI Content Understanding (Chi tiết từng bước cấu hình Analyzer đa phương thức)

> **Mục tiêu:** Nắm vững dịch vụ GenAI đa phương thức thế hệ mới **Azure AI Content Understanding** theo đúng khung kỹ năng cập nhật của đề thi AI-103: từ cấu hình **Single-task vs Pro-mode pipelines**, trích xuất **Structured Output & Markdown**, phân tích video theo phân đoạn thời gian (**Video Segments & Timestamps**), đến tích hợp làm **Foundry Tool** cho Agent và RAG downstream reasoning.

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** **<$0.50** (chỉ test với 1 ảnh, 1 audio ngắn 10s, 1 video 10s; TUYỆT ĐỐI KHÔNG upload file dài).  
**Phạm vi lab:** `rg-ai103-lab` → Azure AI Foundry Project `lqnhat136-8220` → Content Understanding.

---

## 1. Mental Model: GenAI-Native Multimodal Processing

Khác với các dịch vụ Cognitive truyền thống (tách riêng Vision, Speech, Text), **Azure AI Content Understanding** là nền tảng thống nhất đa phương thức được thiết kế để giải quyết bài toán: **Làm sao biến mọi loại nội dung phi cấu trúc (Docs, Images, Audio, Video) thành dữ liệu có cấu trúc JSON hoặc Markdown sạch để LLM/Agent đọc hiểu.**

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      AZURE AI CONTENT UNDERSTANDING PIPELINE                            │
│                                                                                         │
│  ĐẦU VÀO ĐA PHƯƠNG THỨC                ANALYZER ENGINE (GENAI-POWERED)       ĐẦU RA     │
│                                                                              CHUẨN HÓA  │
│  ┌──────────────────────┐              ┌───────────────────────────────┐     ┌────────┐ │
│  │ Documents (PDF, Word)│ ──┐          │ 1. Contextualization Layer    │ ──► │ JSON   │ │
│  ├──────────────────────┤   │          │    (Bóc tách, trích xuất mẫu) │     │ Schema │ │
│  │ Images (PNG, JPG)    │ ──┼────────► │ 2. Reasoning & Generation     │     │ Output │ │
│  ├──────────────────────┤   │          │    (Single-task hoặc Pro-mode)│ ──► ├────────┤ │
│  │ Audio (WAV, MP3)     │ ──┼────────► │ 3. Grounding & Alignment      │     │ Clean  │ │
│  ├──────────────────────┤   │          └───────────────────────────────┘     │ Mark-  │ │
│  │ Video (MP4)          │ ──┘                                                │ down   │ │
│  └──────────────────────┘                                                    └────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Các Khái niệm Trọng tâm trong Đề thi AI-103

### 2.1 Single-task vs Pro-mode Pipelines (Bẫy đề thi mới)

Đề thi AI-103 phân biệt rõ 2 chế độ xử lý trong Content Understanding:

| Chế độ Pipeline | Cơ chế hoạt động | Độ trễ & Chi phí | Trường hợp áp dụng |
| :--- | :--- | :--- | :--- |
| **Single-task Pipeline** | Tập trung thực thi **một tác vụ duy nhất** trên một loại dữ liệu (ví dụ: chỉ trích xuất thông tin người dùng từ ảnh CMND, hoặc chỉ tóm tắt một đoạn audio). | Tốc độ cao, chi phí tối thiểu (chỉ tính 1 lần contextualization). | Các bài toán nghiệp vụ đơn giản, dữ liệu đồng nhất, yêu cầu phản hồi nhanh. |
| **Pro-mode Pipeline** | Cho phép thiết lập **chuỗi xử lý phức tạp (Chained / Multi-stage)** kết hợp nhiều kỹ năng: bóc tách đa phương thức, suy luận logic chuyên sâu (Deep Reasoning), đối chiếu chéo nhiều nguồn thông tin, và kiểm duyệt an toàn. | Chi phí cao hơn, độ trễ lớn hơn do qua nhiều bước xử lý. | Các bài toán phức tạp: Phân tích video an ninh để trích xuất vi phạm kèm thời gian, hoặc thẩm định hồ sơ bảo hiểm gồm cả ảnh hiện trường + hợp đồng scan. |

---

### 2.2 Video Analysis: Xử lý theo Phân đoạn Thời gian (Video Segments & Timestamps)

Khi xử lý Video trong Content Understanding, hệ thống không chỉ "xem" video mà còn chia tách thông minh:
1. **Key-frame Extraction:** Tự động bắt các khung hình mang thông tin quan trọng nhất, loại bỏ các khung hình trùng lặp.
2. **Temporal Segmentation (Phân đoạn theo mốc thời gian):** Gắn nhãn thời điểm bắt đầu (`startTime`) và kết thúc (`endTime`) cho từng sự kiện được phát hiện trong video.
3. **Multimodal Fusion:** Kết hợp hình ảnh hiển thị trên video với lời nói (Speech-to-Text) thu được từ âm thanh của video đó.

---

## 3. Hướng dẫn Từng bước: Khởi tạo và Sử dụng Analyzer (Step-by-Step)

Hiện tại, Content Understanding được quản lý qua REST API hoặc Foundry Studio. Dưới đây là quy trình chuẩn từ định nghĩa Schema đến phân tích:

### Bước 1: Định nghĩa Analyzer Schema (JSON Specification)

Ta muốn phân tích video giám sát an toàn lao động trong công xưởng (phát hiện vi phạm không đội mũ bảo hộ và mặc áo phản quang):

```json
{
  "analyzerId": "safety-compliance-analyzer",
  "scenario": "video",
  "description": "Phân tích video công trường để phát hiện vi phạm an toàn lao động kèm mốc thời gian",
  "fieldSchema": {
    "fields": {
      "overall_safety_status": {
        "type": "string",
        "enum": ["Compliant", "Non-Compliant", "Critical"],
        "description": "Đánh giá mức độ an toàn chung của đoạn video"
      },
      "violations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "timestamp_start": {
              "type": "string",
              "description": "Thời điểm bắt đầu vi phạm (định dạng HH:MM:SS)"
            },
            "timestamp_end": {
              "type": "string",
              "description": "Thời điểm kết thúc vi phạm (định dạng HH:MM:SS)"
            },
            "violation_type": {
              "type": "string",
              "enum": ["Missing Helmet", "Missing Safety Vest", "Unauthorized Area"],
              "description": "Loại vi phạm an toàn phát hiện được"
            },
            "description": {
              "type": "string",
              "description": "Mô tả chi tiết hành vi vi phạm"
            }
          },
          "required": ["timestamp_start", "timestamp_end", "violation_type"]
        },
        "description": "Danh sách các sự cố vi phạm quy chuẩn an toàn lao động"
      }
    }
  }
}
```

---

### Bước 2: Đăng ký Analyzer lên Azure qua REST API / Python

```python
import json
import requests
from azure.identity import DefaultAzureCredential

# Endpoint từ Azure AI Foundry hoặc Cognitive Services
ENDPOINT = "https://<your-foundry-resource>.cognitiveservices.azure.com"
ANALYZER_ID = "safety-compliance-analyzer"
API_VERSION = "2024-12-01-preview"

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default").token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

analyzer_url = f"{ENDPOINT}/contentunderstanding/analyzers/{ANALYZER_ID}?api-version={API_VERSION}"

# Đọc schema từ file cấu hình
with open("safety_analyzer_schema.json", "r") as f:
    analyzer_definition = json.load(f)

# Tạo hoặc cập nhật Analyzer
response = requests.put(analyzer_url, headers=headers, json=analyzer_definition)

if response.status_code in [200, 201]:
    print(f" Đã đăng ký thành công Content Understanding Analyzer: {ANALYZER_ID}")
else:
    print(f" Lỗi đăng ký ({response.status_code}): {response.text}")
```

---

### Bước 3: Gửi File Đa phương thức vào Analyzer và Nhận Kết quả

```python
import time

# Gửi yêu cầu phân tích một video clip ngắn (10 giây)
analyze_url = f"{ENDPOINT}/contentunderstanding/analyzers/{ANALYZER_ID}:analyze?api-version={API_VERSION}"

video_payload = {
    "url": "https://<storage>.blob.core.windows.net/test-videos/safety-clip-10s.mp4"
}

analyze_response = requests.post(analyze_url, headers=headers, json=video_payload)

if analyze_response.status_code == 202:
    # Service trả về header Operation-Location để kiểm tra tiến trình (Async Polling)
    operation_url = analyze_response.headers["Operation-Location"]
    print(" Job phân tích đang chạy, đang kiểm tra trạng thái...")

    while True:
        status_res = requests.get(operation_url, headers=headers).json()
        status = status_res.get("status")
        
        if status == "succeeded":
            print(" Phân tích hoàn tất!\n")
            extracted_fields = status_res["result"]["contents"][0]["fields"]
            print(json.dumps(extracted_fields, indent=2, ensure_ascii=False))
            break
        elif status in ["failed", "canceled"]:
            print(f" Phân tích thất bại: {status_res.get('error')}")
            break
        
        time.sleep(3)
```

---

## 4. Hướng dẫn Thao tác trên Azure AI Foundry Studio UI (No-code Analyzer)

Trong đề thi AI-103, Microsoft thường yêu cầu bạn hiểu cách cấu hình Analyzer và kiểm thử multimodal trực tiếp trên giao diện **Azure AI Foundry Studio** ([ai.azure.com](https://ai.azure.com)):

### 4.1 Quy trình Tạo Analyzer trên Foundry Studio UI (Click-by-click)
1. Đăng nhập [ai.azure.com](https://ai.azure.com), mở Project `lqnhat136-8220`.
2. Trên menu điều hướng bên trái, tìm mục **Tools** $\rightarrow$ chọn **Content Understanding**.
3. Bấm nút **+ Create custom analyzer**.
4. **Cấu hình thông tin cơ bản:**
   - **Analyzer name:** Nhập tên định danh (ví dụ: `workplace-safety-analyzer`).
   - **Select scenario:** Chọn 1 trong 4 loại kịch bản: `Video`, `Audio`, `Images`, hoặc `Documents`.
   - **Pipeline mode (Trọng tâm đề thi):**
     - Chọn `Single-task`: Cho các bài toán trích xuất cơ bản, tối ưu tốc độ và chi phí.
     - Chọn `Pro-mode`: Nếu cần xâu chuỗi nhiều bước suy luận logic sâu (Chained reasoning).
5. **Thiết kế Field Schema trên UI:**
   - Bấm nút **+ Add field**:
     - *Field name:* Nhập tên trường (ví dụ: `violations`).
     - *Field type:* Chọn `Array`.
     - *Items type:* Chọn `Object` để tạo trường lồng nhau.
     - Bấm **+ Add sub-field** để thêm các thuộc tính con: `timestamp_start` (`string`), `timestamp_end` (`string`), `violation_type` (`string`).
     - *Description:* Nhập hướng dẫn cụ thể cho model (ví dụ: *"Xác định thời điểm công nhân không đội mũ bảo hộ"*).
   - Bấm **Save analyzer**.

---

### 4.2 Kiểm thử Đa phương thức Trực quan trên Studio UI
1. Mở Analyzer vừa tạo $\rightarrow$ bấm tab **Test**.
2. **Tải lên dữ liệu:** Kéo thả một video clip ngắn (10 giây) hoặc ảnh mẫu vào khung tải lên.
3. Bấm nút **Run analysis** ở góc trên.
4. **Quan sát các màn hình kết quả:**
   - **Video Player:** Trình phát video tích hợp sẵn các điểm đánh dấu màu đỏ trên thanh timeline tương ứng với các vi phạm phát hiện được.
   - **Fields tab:** Hiển thị trực quan dữ liệu JSON trích xuất thành bảng gồm các cặp key-value rõ ràng.
   - **Markdown tab:** Hiển thị văn bản tài liệu đã được chuẩn hóa và loại bỏ các định dạng rác (Clean Grounded Representation).

---

## 5. Tích hợp Content Understanding làm Foundry Tool cho Agent & RAG

Một kỹ năng cốt lõi trong đề thi AI-103 là: **Dùng Content Understanding để làm sạch dữ liệu (Clean, grounded representation) trước khi gửi vào Agent:**

```text
[Tài liệu scan lộn xộn] ──► Content Understanding ──► [Clean Markdown + JSON Fields]
                                                               │
                                                               ▼
[Foundry Agent / RAG] ◄────────────────────────────────────────┘
(Đọc Markdown sạch để suy luận logic, không bị nhiễu bởi định dạng rác)
```

1. **Clean Markdown Representation:** Content Understanding tự động loại bỏ các khoảng trắng thừa, căn chỉnh lại bảng biểu thành Markdown chuẩn, giúp giảm 40% chi phí token so với text thô từ OCR truyền thống.
2. **Grounding Context:** Agent có thể truy cập kết quả trích xuất của Content Understanding như một **Knowledge Tool**, giúp trả lời các câu hỏi phức tạp về video, audio mà LLM thông thường không thể tự xử lý.

---

## 5. Kiến thức thi trọng tâm (Exam Objectives & Traps)

| Tình huống trong đề thi | Giải pháp / Lựa chọn chính xác |
| :--- | :--- |
| Cần phân tích video clip đào tạo nội bộ để bóc tách các kỹ năng được giảng dạy kèm mốc thời gian bắt đầu và kết thúc | Sử dụng **Content Understanding Analyzer** với kịch bản `video` và định nghĩa trường dạng `array` chứa `timestamp_start` và `timestamp_end`. |
| Muốn giảm thiểu chi phí khi phân tích tài liệu bằng Content Understanding | Cấu hình **Single-task Pipeline** chỉ trích xuất đúng các trường thiết yếu, tránh bật Pro-mode đa tầng nếu không cần suy luận chéo. |
| Chatbot cần trả lời câu hỏi dựa trên cả file ghi âm cuộc họp và slide thuyết trình PDF đính kèm | Sử dụng **Content Understanding trong Foundry Tools** để chuẩn hóa dữ liệu đa phương thức thành Clean Grounded Representation trước khi đưa vào Agent. |
| Làm sao để ép buộc model AI trả về dữ liệu đúng định dạng JSON phục vụ tích hợp hệ thống backend? | Định nghĩa **Field Schema** nghiêm ngặt trong Analyzer với các kiểu dữ liệu (`string`, `number`, `boolean`, `enum`, `object`). |

---

## 6. Definition of Done — Day 8

- [ ] Phân biệt được sự khác nhau giữa Single-task Pipeline và Pro-mode Pipeline trong Content Understanding.
- [ ] Thiết kế được một Field Schema JSON chuẩn hỗ trợ phân đoạn thời gian (Timestamps) cho Video/Audio.
- [ ] Hiểu rõ quy trình đăng ký Analyzer và cơ chế kiểm tra tiến trình (Operation-Location polling).
- [ ] Nắm vững cách tích hợp Clean Markdown từ Content Understanding vào hệ thống RAG và Foundry Agent.
- [ ] Hiểu rõ cơ chế tính phí 2 chặng: Phí Contextualization + Phí Extraction.

---

## Sources (Official, checked 16/09/2026)

- [Azure AI Content Understanding overview](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/overview)
- [Content Understanding Analyzers and Schema](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/concepts/analyzers)
- [Content Understanding Pricing Explainer](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/pricing-explainer)
- [AI-103 Study Guide: Implement Information Extraction Solutions](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)
