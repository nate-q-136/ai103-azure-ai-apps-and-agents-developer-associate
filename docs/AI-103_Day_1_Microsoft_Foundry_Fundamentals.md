# AI-103 — Day 1: Microsoft Foundry Fundamentals

> Mục tiêu: xây đúng mental model về **Microsoft Foundry** trước khi tạo bất kỳ model, agent hay tool nào. Sau Day 1 bạn phải nhìn một tình huống AI-103 và biết nó thuộc Models, Agents, Tools, Knowledge, Observability hay Control Plane.

**Thời lượng gợi ý:** 2.5–3.5 giờ  
**Chi phí:** **$0** — hôm nay không tạo project, Foundry resource, deployment hay gọi API.  
**Prerequisite:** Day 0 hoàn thành: `Azure subscription 1`, `rg-ai103-lab`, budgets và Cost Analysis baseline.

---

## 1. Foundry là gì — và không phải là gì?

Microsoft Foundry là nền tảng Azure hợp nhất để xây, vận hành, tối ưu và govern AI apps/agents: models, agents, tools, tracing, monitoring, evaluations, RBAC, networking và policies nằm trong một management plane. Nó **không phải một model**, không phải chỉ là Azure OpenAI endpoint, và cũng không phải chỉ là một giao diện chat/Playground. [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

```text
Microsoft Foundry = platform / factory
├── Models           → “bộ não” để inference
├── Agents           → model + instructions + tools, có lifecycle
├── Tools/Knowledge  → action và dữ liệu mà agent/model dùng
├── Observability    → trace, monitor, evaluate
└── Control plane    → RBAC, network, policy, governance, inventory
```

So sánh với stack bạn đã biết:

| Khái niệm bạn quen | Microsoft Foundry tương ứng | Điểm khác quan trọng |
|---|---|---|
| OpenAI API provider | Foundry Models / Azure OpenAI | Azure có deployment, region, quota, RBAC và billing scope |
| Agno/LangGraph agent | Foundry Agent Service | Có managed runtime, tools, endpoint, lifecycle/observability |
| Qdrant/RAG store | Azure AI Search / Foundry knowledge tooling | Ngày 5–6 sẽ học sâu retrieval/indexing |
| Tool/function calling | Foundry tools, Toolbox, MCP/custom functions | Có thể centralize auth/governance/versioning |
| Langfuse / tracing | Foundry Observability + Application Insights | Trace, metrics, evaluations cùng nền tảng Azure |
| IAM/OAuth | Microsoft Entra ID + Azure RBAC | Scope theo subscription/RG/resource/project/agent |
| Terraform/IaC | Bicep/ARM/CLI | Control plane Azure, policy và deployment lifecycle |

---

## 2. Kiến trúc phải thuộc

```text
Azure subscription
└── Resource group (rg-ai103-lab)
    └── Foundry resource
        ├── resource-level governance: RBAC, networking, policy, billing
        ├── model deployments
        └── Foundry project(s)
            ├── models / deployments available to the project
            ├── agents, files, evaluations, traces and other assets
            └── developer work boundary
```

| Thành phần | Ý nghĩa | Quyết định exam thường hỏi |
|---|---|---|
| Subscription | Billing/quota boundary lớn | Subscription nào có quota, quyền Owner/Contributor, budget |
| Resource group | Lifecycle/cost/cleanup boundary | Xoá RG xoá toàn bộ lab resources |
| Foundry resource | Ranh giới quản trị top-level | Networking, security, monitoring, model deployments |
| Foundry project | Ranh giới phát triển/use case trong resource | Team, assets, agent workflows/evaluations |
| Project asset | Artefact của use case | Agent, files, evaluation, trace… |

Foundry resource là top-level Azure resource quản lý governance, networking, security và model deployments; project là development boundary bên trong đó. Sự tách lớp này cho phép IT áp control tập trung ở resource level trong khi developer làm việc tại project level. [Foundry architecture](https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture)

### Câu dễ nhầm

- **“Tôi muốn cách ly network/RBAC/policy cho môi trường AI.”** → nghĩ đến **Foundry resource**.
- **“Tôi muốn tách use case/team/assets/evaluations.”** → nghĩ đến **Foundry project**.
- **“Tôi muốn dùng một model cụ thể cho app.”** → cần **model deployment** (Day 2).
- **“Tôi muốn model vừa trả lời vừa gọi tool/tìm dữ liệu.”** → cần **agent + tools/knowledge** (Day 3–4).

---

## 3. Bản đồ năng lực Foundry theo đúng nhu cầu

| Nếu yêu cầu là… | Capability nên nghĩ tới | Lý do |
|---|---|---|
| Chọn/gọi LLM, small model, code model, multimodal model | **Foundry Models** | Catalog + deployment + inference endpoint |
| Tạo trợ lý có instructions, conversation và tool calls | **Foundry Agent Service** | Managed prompt/hosted agent lifecycle |
| Agent cần tìm tài liệu nội bộ | **Knowledge/retrieval** + Azure AI Search/Foundry IQ | Grounding/RAG, không nhét toàn bộ docs vào prompt |
| Agent gọi REST/MCP/file search/code interpreter/web search | **Tools / Toolbox** | Có tool schema, auth, governance, reuse |
| Đo groundedness, relevance, tool-call accuracy hoặc safety | **Evaluations** | Đánh giá trước/ sau release, phát hiện regression |
| Điều tra model/agent đã làm gì, latency/error/token | **Tracing + Monitoring** | Quan sát runtime thực tế |
| Quản trị nhiều project, agents, model/tools | **Foundry Control Plane** | Fleet inventory, compliance/security/observability ở scale |
| Hạn chế content rủi ro và công cụ agent được quyền dùng | **Guardrails/content filters + RBAC/tool controls** | Safety tại runtime và least privilege |

AI-103 đo việc chọn dịch vụ Foundry cho generative task, grounding, vector search, agent workflows, multimodal processing; và chọn memory/tool/knowledge integration phù hợp. [AI-103 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)

---

## 4. Agents: prompt agent và hosted agent

Đừng gọi mọi thứ có LLM là “agent”. Foundry phân biệt mức độ managed/control:

| Kiểu | Bạn cung cấp | Foundry lo | Chọn khi |
|---|---|---|---|
| **Prompt agent** (declarative) | Instructions, model, tools bằng portal/SDK | Runtime/scale/conversation/tool orchestration | Muốn ít code/ops, prototype nhanh, agent chuẩn |
| **Hosted agent** (full code) | Code/framework của bạn đóng container | Endpoint, scaling, identity, observability | Cần logic/framework/custom runtime sâu |
| App gọi model trực tiếp | Prompt + application orchestration | Model inference platform | Không cần agentic lifecycle/tool orchestration managed |

Prompt agent là declarative: bạn khai báo instruction/model/tools, Foundry host/run. Hosted agent là code/container của bạn chạy với managed endpoint, scaling, identity và observability. Có thể bắt đầu prompt agent rồi chuyển dần sang code khi yêu cầu tăng. [What is Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

### Công thức agent để nhớ

```text
Agent = model + instructions + conversation state + tools + knowledge + safeguards
```

- **Model** sinh reasoning/response.
- **Instructions** định vai trò, policy, format, boundaries.
- **Conversation state** giữ context qua nhiều lượt theo lifecycle phù hợp.
- **Tools** thực hiện action hoặc truy cập system/dữ liệu.
- **Knowledge** grounding, retrieval, files/index/search.
- **Safeguards** giới hạn content, quyền tool, approval/oversight khi cần.

Day 3 sẽ build agent; Day 1 chỉ cần nhận diện đúng các mảnh ghép.

---

## 5. Tools và Knowledge: “biết” khác “làm”

```text
Knowledge / retrieval = agent biết gì, dựa vào nguồn nào
Tools               = agent có thể làm gì, gọi hệ thống nào
```

| Requirement | Phân loại đúng | Ví dụ |
|---|---|---|
| Trả lời theo policy PDF nội bộ, có citation | Knowledge/retrieval | Azure AI Search vector/hybrid retrieval |
| Tạo ticket trong hệ thống hỗ trợ | Tool/action | Function/API tool có schema |
| Tính toán từ spreadsheet | Tool | Code interpreter hoặc custom function |
| Lấy dữ liệu CRM đã authorize | Tool + Entra/auth | API/connector với least privilege |
| Nhớ thông tin preference theo hội thoại | Conversation memory/state | Không phải vector search mặc định |

Agent Service có tools chuẩn như file search, code interpreter, web search; toolbox còn có thể curate/reuse tool, MCP server và custom function với authentication/governance/versioning tập trung. [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)

---

## 6. Observability, evaluation và safety: ba thứ không được gộp làm một

| Khả năng | Câu hỏi nó trả lời | Khi dùng |
|---|---|---|
| **Tracing** | “Lần request này agent gọi gì, mất bao lâu, hỏng ở đâu?” | Debug/runtime investigation |
| **Monitoring** | “Hệ thống có đang error/slow/đắt bất thường không?” | Operations liên tục |
| **Evaluation** | “Version/prompt/agent nào tốt và an toàn hơn theo dataset?” | Trước release, regression testing |
| **AI red teaming** | “Có thể khai thác/prompt-inject/đẩy hành vi unsafe không?” | Adversarial safety testing |
| **Guardrails/content filters** | “Runtime có nên chặn/giảm rủi ro output/tool action không?” | Enforce behavior khi chạy |

Foundry có evaluators cho chất lượng tổng quát, RAG (groundedness/relevance), safety/security và agent (tool-call accuracy/task completion). Observability tích hợp Application Insights để theo dõi token, latency, error rate và quality scores. [Foundry Observability](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)

**Exam trap:** evaluation không thay thế production monitoring; content filter/guardrail không thay thế red teaming; trace một request không chứng minh phiên bản mới tốt hơn trên dataset.

---

## 7. Governance và security: mental model “control đúng scope”

```text
Identity (who?) → Microsoft Entra ID
Authorization (can do what?) → Azure RBAC, role + scope
Network (from where?) → public/private networking, private endpoint where required
Data/secret (how protected?) → keyless auth/managed identity, Key Vault, encryption
Policy/oversight (what is allowed?) → Azure Policy, content filters, tool controls, approvals
```

Thứ tự tư duy chuẩn cho case production:

1. Ưu tiên **Entra ID + managed identity/keyless credential** thay key tĩnh.
2. Cấp **least privilege** ở scope hẹp nhất đủ dùng.
3. Chỉ dùng private networking khi scenario yêu cầu network isolation; nó tăng độ phức tạp vận hành.
4. Hạn chế tool quyền cao và thêm approval/oversight cho action nhạy cảm.
5. Trace/audit để điều tra hành vi và đảm bảo accountability.

Foundry áp Microsoft Entra identity, RBAC, content filters, network isolation và Azure Policy trên cùng platform. [What is Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

---

## 8. Terminology hiện hành và tên cũ — cần biết để không rối tài liệu

Microsoft đang chuyển mạnh sang **Microsoft Foundry (new portal)**; nhiều tutorial cũ vẫn dùng Azure AI Foundry/Azure AI Studio/hub hoặc Assistants API.

| Tên cũ / classic | Tên/khái niệm hiện hành | Ý nghĩa cho bạn |
|---|---|---|
| Azure AI Studio / Azure AI Foundry | **Microsoft Foundry** | Dùng portal mới khi học mới |
| Azure AI Services | **Foundry Tools** | Speech/Language/Vision/Document Intelligence… vẫn là capabilities liên quan |
| Hub + nhiều resources | **Foundry resource + projects** | Hướng đầu tư mới, management plane hợp nhất |
| Assistants API; threads/messages/runs | **Responses API; conversations/items/responses** | Đừng lẫn object/API trong Day 2–4 |
| Azure AI User / Owner | **Foundry User / Foundry Owner** | Có thể còn thấy tên cũ khi rollout |

Microsoft nêu rõ new Foundry portal là hướng đầu tư mới; một số capability/classic project còn ở Foundry classic. [Foundry evolution](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

---

## 9. Bài học Day 1 — làm hoàn toàn free, không tạo resource

### Phần A — đọc bản đồ platform (45–60 phút)

1. Đọc [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry), tập trung 4 phần: What you can build, Enterprise-ready platform, Start by building an agent, Evolution.
2. Đọc [Foundry architecture](https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture), tập trung Foundry resource vs project.
3. Mở [Foundry documentation home](https://learn.microsoft.com/en-us/azure/foundry/) để xem taxonomy. **Chỉ đọc; không bấm Create, Deploy hay Start building.**
4. Viết một sơ đồ tay gồm subscription → RG → Foundry resource → project → asset.

### Phần B — “portal tour” read-only (25–35 phút)

1. Vào [ai.azure.com](https://ai.azure.com/) bằng account Azure của bạn.
2. Nếu portal hiện project picker, chỉ quan sát các lựa chọn; **không chọn Create new project** hôm nay.
3. Ghi lại navigation bạn nhìn thấy, thường gồm:
   - **Discover**: models và khả năng để khám phá.
   - **Build**: assets/model/agent của project (sẽ rõ khi có project).
   - **Operate**: quan sát/vận hành, tùy tenant/release.
   - **Manage**: project/resource settings, user/permissions.
4. Nếu portal yêu cầu tạo project mới cho phép xem sâu hơn, dừng tại đó. Đây là bình thường; sẽ tạo chính thức ở Day 2 theo guide để đảm bảo đúng RG, region, model và cost scope.

> Giao diện/nhãn Foundry có thể thay đổi theo release/tenant; hãy bám capability hơn là học thuộc vị trí một nút.

### Phần C — mini design exercise (45 phút)

Đặt case: **“Trợ lý nội bộ trả lời chính sách HR từ PDF, có trích nguồn; nhân viên không được phép tự tạo hay xoá dữ liệu HR.”**

Trả lời bằng 6 dòng trong note của bạn:

1. **Model:** small/mini chat model phù hợp chi phí; chọn ở Day 2.
2. **Knowledge:** Azure AI Search/hybrid retrieval cho PDFs, không paste toàn bộ document vào prompt.
3. **Agent:** prompt agent trước; instructions buộc cite nguồn và không bịa câu trả lời.
4. **Tools:** chưa cần action tool; nếu cần mở ticket, dùng API tool với scope hẹp.
5. **Safety:** content filters + grounding evaluation; deny tool call không cần thiết.
6. **Security:** Entra ID, RBAC least privilege; Foundry resource/project đúng scope; private networking nếu policy yêu cầu.

### Phần D — tự giải 5 câu (20 phút)

1. Cần biết tại sao một agent trả lời sai ở một request cụ thể: **trace**.
2. Cần so sánh groundedness của prompt version A/B trên 200 test cases: **evaluation**.
3. Cần chặn agent gọi API thanh toán nếu chưa được approver xác nhận: **tool access control + approval/oversight**.
4. Cần tổ chức assets cho hai use cases (HR assistant và IT assistant) cùng governance: **hai projects trong một Foundry resource** nếu cùng control boundary.
5. Cần tự host custom LangGraph logic: **hosted agent**, thay vì declarative prompt agent.

---

## 10. Definition of Done — Day 1

- [ ] Mô tả Foundry bằng một câu: platform, không phải model.
- [ ] Vẽ đúng quan hệ subscription → RG → Foundry resource → project → assets.
- [ ] Phân biệt model, agent, tool, knowledge, trace, monitor, evaluation và guardrail.
- [ ] Chọn đúng prompt agent vs hosted agent theo yêu cầu control/ops.
- [ ] Giải thích knowledge/retrieval khác tool/action.
- [ ] Nhận ra terminology cũ vs mới (Studio/Foundry, Assistants/Responses, hub/resource).
- [ ] Hoàn thành design exercise HR với tối thiểu model + retrieval + security + evaluation.
- [ ] Chưa tạo resource/deployment hoặc phát sinh model usage cost.

---

## 11. Tài liệu chính thức đã đối chiếu (14/09/2026)

- [AI-103 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)
- [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)
- [Microsoft Foundry architecture](https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture)
- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Foundry Observability](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability)
- [Foundry capability map](https://learn.microsoft.com/en-us/azure/foundry/concepts/capabilities)

---

## Handoff sang Day 2

Day 2 mới tạo project, Foundry resource và một model deployment nhỏ trong `rg-ai103-lab`. Làm guide này trước: [AI-103 Day 2 — Foundry Models / Azure OpenAI](AI-103_Day_2_Foundry_Models_Azure_OpenAI.md).
