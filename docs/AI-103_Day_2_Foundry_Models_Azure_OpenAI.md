# AI-103 — Day 2: Foundry Models / Azure OpenAI

> Mục tiêu: hiểu **đường đi từ Azure đến một lời gọi model an toàn, có kiểm soát chi phí**, sau đó tự tạo một deployment nhỏ và gọi nó từ Playground lẫn Python. Đây là phần trọng tâm của AI-103, không phải chỉ là “biết gọi API”.

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** khoảng **$0.50–$2** cho vài lần thử nhỏ.  
**Phạm vi lab:** subscription `Azure subscription 1`, resource group `rg-ai103-lab`, budget đã tạo ở Day 0.

> Trạng thái kiến thức vào Day 2: bạn đã có subscription hoạt động, resource group `rg-ai103-lab` ở Southeast Asia, budget/alerts, và Cost Analysis baseline. Không cần tạo VM, GPU, AKS, Azure AI Search hay Agent Service hôm nay.

---

## 1. Vì sao Day 2 quan trọng cho AI-103?

Study guide AI-103 (skills measured từ 16/04/2026) yêu cầu bạn biết chọn deployment option, cấu hình model/agent deployment, và quản lý quota, scaling, rate limit, cost footprint; đồng thời dùng managed identity, keyless credentials và role policies. [Study guide AI-103](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)

Vì vậy, khi gặp câu hỏi tình huống, hãy suy luận theo chuỗi này:

```text
Yêu cầu nghiệp vụ / dữ liệu / lưu lượng
        ↓
Chọn model phù hợp
        ↓
Chọn kiểu deployment và vùng xử lý dữ liệu
        ↓
Kiểm tra region + quota
        ↓
Triển khai với tên deployment rõ ràng
        ↓
Xác thực (Entra ID ưu tiên) + RBAC tối thiểu
        ↓
Quan sát token / chi phí / lỗi rate limit
```

**Không nhầm lẫn các tên sau:**

| Khái niệm | Nghĩa thực tế | Ví dụ trong lab |
|---|---|---|
| Model | Năng lực gốc trong catalog | `gpt-5-mini` (nếu catalog của bạn có) |
| Model version | Phiên bản cố định của model | Do portal hiển thị; không tự đoán |
| Deployment | Bản model được expose để ứng dụng gọi | `ai103-chat-mini` |
| Deployment name | Giá trị truyền vào `model=` trong code | `ai103-chat-mini`, **không nhất thiết** là tên model |
| Foundry resource | Azure resource: ranh giới billing, identity, network, monitoring | resource tự tạo khi tạo project |
| Foundry project | Không gian làm việc chứa assets/developer workflow | `ai103-day2-project` |
| Endpoint | URL để client gọi model | `https://<resource>.openai.azure.com/openai/v1/` |
| Quota | Sức chứa tối đa Azure cấp cho subscription | TPM theo model/region/deployment type |
| Rate limit | Ngưỡng request/token deployment thực tế được phép gửi | TPM và RPM |

Model deployment trong một Foundry resource có thể được thử bằng Playground và gọi từ code. Tên **deployment** mới là giá trị dùng để route request trong tham số `model`. [Deploy Foundry Models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/deploy-foundry-models)

---

## 2. Mental model phải thuộc

```text
Azure subscription
└── rg-ai103-lab                    ← cost scope / cleanup boundary
    └── Microsoft Foundry resource  ← endpoint, IAM, billing, networking
        └── Foundry project         ← nơi bạn build/test
            └── Model deployment    ← tên gọi từ code + quota phân bổ
                └── Responses API / Playground / application
```

Một Foundry resource là ranh giới Azure-managed cho identity, access control, network, security, billing và monitoring. Project là nơi tổ chức model, agent và work của developer. [Create a Foundry resource](https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource)

---

## 3. Lý thuyết cốt lõi: chọn model trước, đừng chọn “model mạnh nhất”

Chọn model theo **task + chất lượng + latency + token cost + region/quota + yêu cầu dữ liệu**.

| Nhu cầu | Hướng chọn trong exam | Lý do |
|---|---|---|
| Chat/RAG thông thường, prototype rẻ | Mini/small chat model khả dụng | Đủ tốt, giảm input/output token cost và latency |
| Suy luận/phân tích khó, cần chất lượng cao | Model reasoning/flagship phù hợp | Đổi chi phí/latency lấy chất lượng |
| Ảnh + text | Multimodal model | Không tự OCR/serialize ảnh nếu model phải hiểu ảnh |
| Embedding cho vector search | Embedding model | Không dùng chat model làm embedding |
| Tác vụ lớn, không cần realtime | Batch deployment | Chi phí thấp hơn, đổi lại async/turnaround |
| Fine-tune evaluation | Developer deployment nếu model hỗ trợ | Mục tiêu chuyên biệt; không có SLA |

Model catalog thay đổi theo region và thời điểm. Trong lab, **không hard-code tên/version từ một blog hay guide**: mở catalog, xem model card, pricing và deployment types mà portal đang cho phép. Bạn chỉ triển khai model mà bạn thấy `Available` cho project của mình.

---

## 4. Deployment types: bảng quyết định thi cử

Foundry có hai nhóm chính: **Standard** (pay-per-token) và **Provisioned** (reserved capacity/PTU). Mỗi nhóm có cách xử lý dữ liệu global, data zone hoặc regional tùy type. [Deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)

| Type | Dữ liệu inference được xử lý ở đâu | Cách trả tiền | Dùng khi | Không chọn khi |
|---|---|---|---|---|
| **Global Standard** | Có thể ở Azure region bất kỳ | Pay-per-token | Prototype, traffic bursty, không bị ràng buộc residency; thường quota mặc định cao | Bắt buộc single-region/data-zone |
| **Data Zone Standard** | Trong data zone Microsoft (US/EU/APAC) | Pay-per-token | Cần boundary data zone nhưng vẫn cần throughput tốt | Bắt buộc đúng một Azure region |
| **Standard** (regional) | Một region deployment | Pay-per-token | Lab lưu lượng thấp, hoặc compliance yêu cầu single region | Cần throughput ổn định rất cao |
| **Global/Data Zone/Regional Provisioned** | Theo global/zone/region | PTU capacity đã reserve | Lưu lượng lớn, ổn định, latency variance thấp | Lab và workload nhỏ, biến động |
| **Global/Data Zone Batch** | Theo global/zone | Theo batch, async | Job lớn không cần realtime; target turnaround 24h | Chat/request tương tác |
| **Managed compute** (preview) | GPU dedicated do Foundry quản lý | Theo giờ accelerator | Host open-source/custom model | Lab tiết kiệm chi phí — có thể phát sinh tiền ngay cả khi không gọi |

### Quy tắc cần nhớ

- **Global** không có nghĩa “data lưu ở mọi nơi”; phần data *at rest* vẫn ở Azure geography đã chọn, còn prompt/response *inference processing* có thể được xử lý ở bất kỳ region Azure nào phù hợp.  
- **Data Zone** giới hạn inference trong zone Microsoft; hiện có US, EU và APAC.  
- **Standard** là pay-per-token, phù hợp lab; triển khai Standard không phải là mua PTU.  
- **Provisioned** là reserve throughput units để có throughput/latency dự đoán hơn; đừng chọn trong Day 2.  
- **Managed compute** là GPU capacity theo giờ, hoàn toàn không phù hợp mục tiêu $5–10 của roadmap.

Global Standard có quota mặc định cao và routing toàn cầu; Standard regional pay-per-token phù hợp low-to-medium volume. Provisioned cấp capacity dự trữ, có latency nhất quán hơn. [Deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)

### Quyết định lab hôm nay

1. **Ưu tiên:** model mini/chat được Foundry sold by Azure hỗ trợ + **Global Standard**, nếu portal cho phép và bạn không có yêu cầu residency.
2. **Fallback:** model mini/chat + **Standard** ở region project nếu Global Standard không hiện.
3. **Tuyệt đối không chọn:** Provisioned/PTU, Batch, managed compute, partner/community model cần Azure Marketplace subscription.

Tên gợi ý cho deployment: `ai103-chat-mini`. Nó khiến code/dashboards rõ mục đích và dễ xoá đúng tài nguyên sau này.

---

## 5. Quota, TPM và RPM — phần rất hay bị nhầm

### 5.1 Quan hệ đúng

```text
Subscription quota (per region + per model + per deployment type)
        ↓ phân bổ TPM khi tạo deployment
Deployment rate limits
        ├── TPM (tokens per minute)
        └── RPM (requests per minute, tỷ lệ theo model)
```

Quota Azure OpenAI được cấp theo **subscription, region, model và deployment type**, với đơn vị TPM. Khi tạo deployment, bạn cấp một phần TPM từ quota; tổng TPM đã phân bổ không được vượt quota cùng tổ hợp đó. RPM được suy ra theo TPM và tỷ lệ có thể khác giữa các model. [Manage Azure OpenAI quota](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/quota)

### 5.2 Suy luận tình huống

| Tình huống | Câu trả lời / hành động đúng |
|---|---|
| Tạo deployment báo `Quota exceeded` | Giảm TPM đã cấp cho deployment khác, hoặc request quota increase; không phải chỉ retry API |
| API trả 429/rate limit | Giảm concurrent traffic, retry bằng exponential backoff, giảm token/request hoặc tăng/phân bổ quota phù hợp |
| Cần quota cao nhất, không ràng buộc data residency | Xem Global Standard trước |
| Cần độc quyền/throughput ổn định | Xem Provisioned, tính PTU và chi phí trước |
| Cần biết quota còn lại nhưng không được quản trị tài nguyên | Role tối thiểu để xem quota là **Cognitive Services Usages Reader** |

**Không nhầm `budget` với `quota`:** quota/rate limit chặn tốc độ/capacity; Azure budget chủ yếu gửi cảnh báo chi phí, không tự tắt model hay resource.

---

## 6. Authentication và RBAC: cách làm đúng

| Cách | Khi nào dùng | Điểm cần nhớ |
|---|---|---|
| API key | Playground/prototype local rất ngắn | Đừng commit key, đừng dán vào source; rotate nếu lộ |
| Microsoft Entra ID + `DefaultAzureCredential` | App thực tế, CI/CD, workload Azure | **Ưu tiên** keyless auth; dùng managed identity khi code chạy trên Azure |
| Managed identity | App chạy trong Azure | Không cần lưu secret; cấp role cho identity đúng scope |

Với Foundry Models, Microsoft khuyến nghị Entra ID. Endpoint OpenAI-compatible dùng `https://<resource>.openai.azure.com/openai/v1/` hoặc `https://<resource>.services.ai.azure.com/openai/v1/`; token scope là `https://ai.azure.com/.default`. Sau khi mọi client đã hỗ trợ keyless auth, bạn có thể disable key-based authentication. [Configure keyless auth](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-entra-id)

Về quyền, hãy phân biệt:

- **Owner/Contributor**: control plane Azure (tạo/manage resource); không mặc nhiên là data-plane developer access trong Foundry.
- **Foundry User**: least-privilege cho developer build/test trong project.
- **Foundry Agent Consumer**: chỉ tương tác endpoint agent.
- **Foundry Project Manager / Foundry Owner**: phạm vi cao hơn để quản lý/publish.

Trong lab cá nhân bạn đang là subscription Owner nên không cần tự cấp role. Trong đề thi/production, cấp role nhỏ nhất ở scope nhỏ nhất. Foundry roles đã đổi tên gần đây; một số màn hình còn hiện tên cũ Azure AI User/Owner nhưng role IDs và core permissions không đổi. [Foundry RBAC](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)

---

## 7. Lab thực hành — triển khai một model nhỏ

### 7.1 Checkpoint chi phí trước khi tạo

1. Vào Azure Portal → **Resource groups** → `rg-ai103-lab`.
2. Vào **Cost Management** → **Cost analysis**. Xác nhận current cost/forecast còn hợp lý và budget vẫn hoạt động.
3. Mở tab mới: [Microsoft Foundry](https://ai.azure.com/). Đăng nhập **cùng account và directory** có `Azure subscription 1`.
4. Nếu Foundry hỏi directory/subscription, chọn đúng subscription. Nếu không thấy, kiểm tra portal ở góc trên phải và switch directory.

> Bạn có thể tạo Foundry resource ở một region khác với location metadata của resource group. Tuy nhiên hôm nay chọn region theo lựa chọn Foundry portal và availability của model; đừng cố ép một model/version không khả dụng ở Southeast Asia.

### 7.2 Tạo project (thao tác này tạo/đi kèm Foundry resource)

1. Trong Foundry, bật **New Foundry** nếu thấy toggle.
2. Ở project picker góc trên trái, chọn **Create new project**.
3. Điền Project name: `ai103-day2-project`.
4. Mở **Advanced options**.
5. Chọn Resource group: **`rg-ai103-lab`**.
6. Chọn Location. Dùng location mà Foundry cho chọn và có model mini bạn sẽ deploy. Nếu Southeast Asia không có combination phù hợp, chọn region được portal hỗ trợ; ghi lại lý do trong notes.
7. Chọn **Create project** và chờ overview hiện ra.
8. Kiểm tra: copy Project endpoint ở welcome screen để biết nó có dạng `https://<resource>.services.ai.azure.com/api/projects/<project>`.

Portal có thể tự tạo Foundry resource nền cho project. Resource này là ranh giới billing/identity; nhờ đặt trong `rg-ai103-lab`, mọi thành phần lab vẫn nằm trong cleanup boundary. [Create a project](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects)

### 7.3 Khám phá catalog trước khi deploy

1. Chọn **Discover** (góc trên) → **Models**.
2. Lọc/search một model mini/chat từ Microsoft/Azure OpenAI đang **Available**. `gpt-5-mini` chỉ là ví dụ, **không phải tên bắt buộc**.
3. Mở model card và ghi vào notes:
   - model name, version và publisher;
   - input/output modalities;
   - context window (nếu card hiển thị);
   - deployment types đang khả dụng;
   - pricing link/estimate;
   - vùng/quota mà portal báo.
4. Đọc phần deployment settings trước khi bấm create. Với model partner/community, nếu portal yêu cầu accept Azure Marketplace terms, **dừng lại** và chọn model sold by Azure khác — tránh bất ngờ billing/terms cho lab.

### 7.4 Deploy an toàn

1. Trên model card, chọn **Deploy → Custom settings**. Chọn custom để bạn thực sự nhìn và hiểu type/quota.
2. Đặt **Deployment name**: `ai103-chat-mini`.
3. Chọn **Global Standard** nếu portal hỗ trợ. Nếu không, chọn **Standard**. Không chọn Provisioned hoặc managed compute.
4. Giữ quota/capacity nhỏ nhất portal cho phép, đủ test vài request. Đừng cấp quota lớn chỉ vì có sẵn.
5. Kiểm tra phần giá/usage summary một lần nữa rồi chọn **Deploy**.
6. Chờ provisioning. Khi xong, portal chuyển tới Playground hoặc Models list; status phải là succeeded/ready.

Nếu model, version, SKU hoặc region không hợp lệ, deployment báo failed. Cách sửa đúng là xem availability/model card và quota, không retry liên tục. [Deploy a Foundry Model](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/deploy-foundry-models)

### 7.5 Test ở Playground: chỉ ba request ngắn

Mở deployment trong Playground và gửi lần lượt:

```text
1. Trả lời đúng một câu: Azure resource group là gì?
2. So sánh Standard với Provisioned deployment bằng bảng 3 dòng.
3. Trả về JSON hợp lệ có các keys: deployment_type, billing, best_for.
```

Kiểm tra 4 điều:

- Response đến từ đúng deployment `ai103-chat-mini`.
- Model theo instruction cơ bản.
- Output JSON ở request 3 có thể parse (chưa cần perfect structured output feature).
- Bạn thấy token/usage hoặc estimated cost ở dashboard sau một lúc.

**Dừng tại đây nếu bạn chỉ muốn học portal.** Ba request ngắn đủ chứng minh deployment hoạt động và giữ chi phí nhỏ.

---

## 8. Gọi bằng Python — chọn một trong hai cách

### 8.1 Chuẩn bị local environment

Tại một thư mục code **ngoài folder `docs`**, tạo/activate virtual environment theo cách bạn thường dùng, rồi cài packages:

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai azure-identity
az login
az account set --subscription "Azure subscription 1"
```

Không copy key vào source file, Markdown, terminal history chung hoặc Git. Thêm `.env` vào `.gitignore` nếu sau này bạn dùng key cho prototype.

### 8.2 Khuyến nghị: Entra ID (keyless)

Tạo file local `day2_hello_foundry.py` và thay hai placeholder. `MODEL_DEPLOYMENT_NAME` là **deployment name**, không phải base model name.

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

RESOURCE_NAME = "<ten-foundry-resource-cua-ban>"
MODEL_DEPLOYMENT_NAME = "ai103-chat-mini"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default",
)

client = OpenAI(
    base_url=f"https://{RESOURCE_NAME}.openai.azure.com/openai/v1/",
    api_key=token_provider,
)

response = client.responses.create(
    model=MODEL_DEPLOYMENT_NAME,
    input="Trong 2 câu tiếng Việt, giải thích sự khác nhau giữa quota và budget trên Azure.",
)

print(response.output_text)
```

Chạy:

```bash
python day2_hello_foundry.py
```

`DefaultAzureCredential` sẽ dùng credential bạn có sau `az login` khi chạy local; khi chạy trên Azure, nó nên dùng managed identity đã được cấp quyền. Microsoft có ví dụ chính thức cùng OpenAI SDK/Responses API và scope trên. [Keyless authentication code](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-entra-id)

### 8.3 Chỉ để hiểu: API key prototype

Không cần làm bước này nếu Entra ID chạy. Với key, client dùng biến môi trường `AZURE_OPENAI_API_KEY` thay vì hard-code; Entra ID vẫn là hướng được khuyến nghị cho app thực tế. [Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)

### 8.4 Khi nhận lỗi

| Triệu chứng | Nguyên nhân hay gặp | Cách xử lý |
|---|---|---|
| `401` / credential failed | Chưa `az login`, sai tenant, hoặc token scope | login lại; kiểm tra subscription/directory; dùng scope `https://ai.azure.com/.default` |
| `403` | Identity không có data-plane role phù hợp | Lab cá nhân: kiểm tra resource IAM; team: cấp Foundry User/Cognitive Services User theo scenario docs |
| `404` model/deployment not found | Dùng base model name thay deployment name, sai endpoint | dùng `ai103-chat-mini`; copy endpoint đúng resource |
| `429` | Hết/quá rate limit TPM/RPM | exponential backoff, giảm request/token, kiểm tra quota allocation |
| Deploy fail | Model/version/type không có ở region, thiếu quota | quay về model card/availability, chọn combination khác hoặc reallocate quota |

---

## 9. Quản lý chi phí đúng cách sau lab

1. Trong Foundry: **Build → Models → chọn model → Monitor**. Xem token/request và estimated cost nếu giao diện có.
2. Trong Azure Portal: `rg-ai103-lab` → **Cost Management → Cost analysis** → group by **Resource**, sau đó **Meter** nếu dữ liệu đã xuất hiện.
3. Ghi vào notes: model, deployment type, số request test, estimated cost và thời gian check.
4. Giữ deployment nếu bạn sẽ dùng ngay Day 3 (Agent Service) trong 1–2 ngày tới. Nếu nghỉ lâu hoặc muốn dừng toàn bộ rủi ro, delete deployment hay toàn bộ resource group.

Estimated cost trong Foundry có thể gần real-time, còn Azure Cost Management/invoice có thể đến chậm và là nguồn để reconcile cuối cùng. Các con số token/request đôi khi lệch tạm thời do ingestion/aggregation. [Plan and manage costs](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs)

> Standard pay-per-token không có “idle GPU” như managed compute, nhưng **mọi API request vẫn có thể phát sinh token charge**. Budget alert không phải circuit breaker — vì vậy vẫn giới hạn số test của bạn.

---

## 10. Exam traps — tự kiểm tra trước khi sang Day 3

1. Một công ty cần traffic bursty, ít vận hành và không có data-residency restriction. Chọn gì?  
   **Global Standard**, vì pay-per-token và quota/routing phù hợp general workload.

2. Công ty bắt buộc inference chỉ ở một region cụ thể. Chọn gì?  
   **Standard regional** (hoặc Regional Provisioned nếu tải lớn/ổn định), không phải Global.

3. Cần high, predictable throughput và latency variance thấp cho tải ổn định. Chọn gì?  
   **Provisioned throughput**, sau khi tính PTU/cost; không dùng cho lab nhỏ.

4. App gửi hàng triệu request không cần phản hồi ngay. Chọn gì?  
   **Batch**, đổi realtime lấy chi phí thấp hơn/asynchronous processing.

5. Developer chỉ cần gọi model deployed sẵn trong project. Nên cấp gì?  
   **Foundry User** ở project scope, không phải Owner subscription.

6. `model="gpt-..."` trả 404 dù model tồn tại trong catalog. Lỗi gì?  
   Code cần **deployment name** mà bạn đã tạo; base model name và deployment name là hai khái niệm khác nhau.

---

## 11. Definition of Done — Day 2

Chỉ đánh dấu hoàn thành khi bạn có đủ:

- [ ] Diễn giải được model vs deployment vs endpoint vs project.
- [ ] So sánh được Global Standard, Data Zone Standard, Standard và Provisioned theo data processing, billing, latency/capacity.
- [ ] Giải thích đúng quota/TPM/RPM và budget khác nhau thế nào.
- [ ] Tạo project trong `rg-ai103-lab`.
- [ ] Tạo đúng **một** deployment mini/chat pay-per-token: `ai103-chat-mini` (hoặc tên bạn ghi lại).
- [ ] Test 3 request ngắn ở Playground.
- [ ] Gọi thành công 1 request từ Python bằng Entra ID, hoặc ghi rõ blocker/RBAC error và nguyên nhân.
- [ ] Kiểm tra Monitor/Cost Analysis, không có managed compute hoặc PTU deployment.
- [ ] Biết giữ deployment cho Day 3 hay xoá nó nếu nghỉ lâu.

---

## 12. Tài liệu chính thức đã đối chiếu (14/09/2026)

- [AI-103 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)
- [Create Foundry resources, project and deployment quickstart](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources)
- [Foundry Models deployment types](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types)
- [Deploy Foundry Models in portal](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/deploy-foundry-models)
- [Azure OpenAI quota](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/quota)
- [Entra ID / keyless authentication](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-entra-id)
- [Foundry RBAC](https://learn.microsoft.com/en-us/azure/foundry/concepts/rbac-foundry)
- [Foundry cost management](https://learn.microsoft.com/en-us/azure/foundry/concepts/manage-costs)

---

## Handoff sang Day 3

Giữ lại duy nhất deployment `ai103-chat-mini` nếu bạn dự định làm Day 3 trong 48 giờ: nó sẽ là model cho Foundry Agent Service. Nếu không, xoá deployment/project/resource group để đóng chi phí, rồi Day 3 tạo lại theo cùng nguyên tắc.

Guide tiếp theo: [AI-103 Day 3 — Foundry Agent Service](AI-103_Day_3_Foundry_Agent_Service.md).
