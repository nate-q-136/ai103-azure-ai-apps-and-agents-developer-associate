# AI-103 — Day 3: Foundry Agent Service

> Mục tiêu: tự xây một **prompt agent** nhỏ dùng deployment Day 2, hiểu đúng vòng đời **agent → conversation → response**, và biết khi nào agent là lựa chọn đúng hơn việc app gọi model trực tiếp.

**Chi phí mục tiêu:** $0.02–$0.15; tối đa 5–8 request ngắn, không bật tool.  
**Phạm vi lab:** `Azure AI-103 Learning` → `rg-ai103-lab` → Foundry project hiện có → deployment `ai103-chat-mini` (Global Standard).  
**Prerequisite đã đạt:** Day 2 deployment, Playground, keyless Python request, Monitor và Cost Analysis đều thành công.

## 1. Mental model phải thuộc

```text
Prompt agent = model + instructions + optional tools/safeguards

Agent        = reusable, persisted behaviour
Conversation = persisted multi-turn state
Response     = một lần runtime xử lý input và tạo output
```

Đừng dùng agent chỉ vì app có chat UI. Nếu một request stateless, không có tool, không cần managed state hay lifecycle riêng, app gọi deployment trực tiếp (Day 2) thường đơn giản hơn. Dùng Agent Service khi instructions/tool configuration/conversation cần được tái sử dụng và quản lý như một asset.

## 2. Những gì Day 3 làm — và chưa làm


| Hôm nay                                                                        | Để ngày sau                                        |
| ------------------------------------------------------------------------------ | -------------------------------------------------- |
| Prompt agent, instructions, conversation, response, agent version, trace/usage | Custom function và MCP (Day 4)                     |
| Streaming response và per-request token usage                                  | Background mode và long-running workloads          |
| Cách hạn chế scope của agent bằng instruction                                  | Knowledge/RAG, AI Search, citations (Days 5–6)     |
| Tình huống Foundry User / Foundry Agent Consumer                               | Workflow, approval flow, multi-agent orchestration |


Không bật Web search, File search hoặc Code Interpreter trong lab này. Các tool đó làm lẫn bài học về tool authorization/cost với vòng đời agent cơ bản.

## 3. Kiến thức thi cốt lõi


| Yêu cầu trong scenario                                            | Chọn / giải thích                                          |
| ----------------------------------------------------------------- | ---------------------------------------------------------- |
| Reuse một persona, model, instructions và tools cho nhiều request | Prompt agent                                               |
| Follow-up cần biết các lượt trước                                 | Tạo/reuse conversation                                     |
| Chạy một lần tạo output từ agent/conversation                     | Response                                                   |
| Developer tạo/sửa agent trong project                             | Foundry User tại project scope                             |
| Client chỉ gọi endpoint agent có sẵn                              | Foundry Agent Consumer, không phải Owner                   |
| Cần code/framework/container riêng                                | Hosted agent, không phải prompt agent                      |
| Cần retrieval từ tài liệu nội bộ                                  | Knowledge/RAG, không nhét toàn bộ tài liệu vào instruction |


**Exam trap:** agent, conversation và response không đồng nghĩa. Agent là definition; conversation giữ lịch sử; response là execution. Conversation không phải “memory vô hạn”: nó có dữ liệu persisted và model chỉ nhận lượng context phù hợp context window.

## 4. Lab portal: tạo prompt agent

### 4.1 Checkpoint trước khi tạo

1. Azure Portal → `rg-ai103-lab` → **Cost analysis**: xác nhận vẫn dưới budget.
2. Microsoft Foundry → chọn đúng project đang chứa `ai103-chat-mini`.
3. Không tạo resource group, deployment, storage, Search, VM hay managed compute mới.

### 4.2 Tạo agent

1. Trong Foundry, chọn **Agents** → **Create agent** (tên nút có thể thay đổi nhẹ).
2. Chọn **Prompt agent**, không chọn Hosted agent.
3. Agent name: `ai103-day3-policy-coach`.
4. Model/deployment: chọn `ai103-chat-mini`.
5. Không thêm Tools, Knowledge, Memory hoặc Guardrails ở lab đầu tiên.
6. Dùng instructions dưới đây và tạo/save agent:

```text
Bạn là AI-103 Policy Coach. Chỉ trả lời về Microsoft Foundry, Azure AI,
model deployments, quota, budget, identity và RBAC.

Trả lời bằng tiếng Việt, tối đa 3 câu. Nếu câu hỏi nằm ngoài phạm vi,
nói rõ bạn chỉ hỗ trợ chủ đề AI-103/Azure AI và đề nghị người dùng đặt lại câu hỏi.
Không bịa nguồn, không dùng web search và không khẳng định cấu hình Azure cụ thể
khi chưa được cung cấp dữ liệu.
```

Ghi lại agent name, model deployment, project endpoint và agent version đang hiển thị. Một thay đổi runtime như instructions/model/tool có thể tạo agent version mới; đây là lý do production cần versioning và evaluation trước khi promote.

### 4.3 Test ngắn trong Playground

Tạo **một conversation mới**, sau đó gửi tuần tự các message:

```text
1. Trong tối đa 3 câu, model deployment và agent khác nhau thế nào?
2. Vậy khi nào tôi chỉ cần gọi deployment trực tiếp?
3. Hãy dự báo giá cổ phiếu Microsoft tuần tới.
```

Kết quả mong đợi:

- Câu 1 có sự phân biệt giữa model deployment (inference endpoint) và agent (reusable orchestration definition).
- Câu 2 nhận diện được case stateless/simple là gọi deployment trực tiếp.
- Câu 3 từ chối/redirect theo scope instruction, không cố trả lời tài chính.
- Câu 2 phải có ý nghĩa theo Câu 1: đó là bằng chứng conversation state hoạt động.

Không lặp request nếu output không hoàn hảo. Ghi lỗi/điểm mơ hồ vào notes; prompt iteration có chủ đích mới là học, không phải “retry đến khi đẹp”.

## 5. Python keyless (optional nhưng nên làm)

Chỉ làm sau khi Portal test xong. Dùng cùng `az login` từ Day 2; không dùng API key.

```bash
uv add "azure-ai-projects>=2.3.0"
```

Tạo `labs/day-3/hello_agent.py`. Lấy **Project endpoint** từ Foundry welcome screen:

```text
https://<resource>.services.ai.azure.com/api/projects/<project>
```

Mẫu code dưới dùng agent đã tạo trong portal; thay endpoint, không hard-code secret:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

PROJECT_ENDPOINT = "https://<resource>.services.ai.azure.com/api/projects/<project>"
AGENT_NAME = "ai103-day3-policy-coach"

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client(agent_name=AGENT_NAME)

conversation = openai.conversations.create()

first = openai.responses.create(
    conversation=conversation.id,
    input="Model deployment và agent khác nhau thế nào?",
)
print(first.output_text)

second = openai.responses.create(
    conversation=conversation.id,
    input="Khi nào chỉ cần gọi deployment trực tiếp?",
)
print(second.output_text)
```

Mẫu này cần Azure AI Projects **2.x**. Nếu API/SDK báo khác tên method, kiểm tra version trước; không trộn code Azure AI Projects 1.x/classic với project (new) API. Mục tiêu Day 3 là hiểu project client + agent-bound OpenAI client + conversation, không phải học thuộc SDK preview.

## 6. Streaming response + token usage (Python, một request ngắn)

Streaming chỉ thay đổi **cách client nhận output**: text được in dần thay vì chờ toàn bộ response. Nó không tự làm inference rẻ hơn, không thay thế conversation, và vẫn tính input/output tokens như response thường.

Thêm đoạn này vào cuối `labs/day-3/hello_agent.py` (hoặc tạo `stream_agent.py`). Đoạn code này không dùng web search/tool:

```python
print("\n--- Streaming response ---")

# Dùng client project và reference rõ agent; cùng conversation ở test trước.
stream_client = project.get_openai_client()
stream = stream_client.responses.create(
    conversation=conversation.id,
    extra_body={
        "agent_reference": {
            "name": AGENT_NAME,
            "type": "agent_reference",
        }
    },
    input="Trong đúng 2 câu, giải thích streaming response hữu ích cho chat UI thế nào.",
    stream=True,
)

completed_response = None
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.completed":
        completed_response = event.response

print("\n--- Usage của request streaming ---")
usage = getattr(completed_response, "usage", None)
if usage:
    print(f"Input tokens:  {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    print(f"Total tokens:  {usage.total_tokens}")
else:
    print("Usage chưa xuất hiện trong SDK response; kiểm tra Foundry Monitor sau vài phút.")
```

`response.output_text.delta` là event cần render trong chat UI. `response.completed` chứa response hoàn tất; code chỉ đọc usage khi nó có mặt để không fail nếu phiên bản SDK trả event khác. Streaming thêm đúng một request vào lab, nên không retry chỉ để xem text chạy lại.

## 7. Metrics, tokens, cost và cleanup

1. Trước streaming, ghi số **Total requests**, **Input tokens**, **Output tokens** và **Estimated total cost** trong Foundry → Agent/Model → **Monitor**.
2. Chạy một request streaming, đợi 1–5 phút, rồi refresh Monitor và ghi delta. Delta phải xấp xỉ tokens Python vừa in; Monitor có thể aggregate/trễ nên không cần khớp tuyệt đối ngay.
3. Azure Portal → `rg-ai103-lab` → Cost analysis → group by **Resource**, sau đó **Meter**. Chỉ mong đợi model input/output tokens.
4. Ghi note theo mẫu:


| Metric                          | Trước | Sau | Delta |
| ------------------------------- | -----: | ---: | -----: |
| Total requests                  |       |     |       |
| Input tokens                    |       |     |       |
| Output tokens                   |       |     |       |
| Foundry estimated cost (USD)    |       |     |       |
| Cost Analysis actual cost (USD) |       |     |       |


5. Python/SDK cho bạn token usage của request; **Foundry Monitor** là nơi xem estimated cost gần real-time. **Azure Cost Analysis** là số dùng để reconcile billing nhưng có độ trễ. Không hard-code công thức USD/token vì model/version, cached tokens, tool usage và giá có thể thay đổi.
6. Xóa test conversations/data nếu không cần. Giữ agent và deployment chỉ khi học Day 4 trong 48 giờ; nếu nghỉ lâu thì xóa agent/deployment hoặc cả RG theo Day 0.

Budget là cảnh báo, không phải công tắc tắt chi phí. Agent Service stateful; conversation, response hoặc file data không nên bị bỏ quên sau lab.

## 8. Definition of Done — Day 3

- [x] Phân biệt được direct model call, prompt agent và hosted agent.
- [x] Giải thích được agent vs conversation vs response.
- [x] Tạo `ai103-day3-policy-coach` dùng deployment `ai103-chat-mini`.
- [ ] Test một conversation có follow-up phụ thuộc lịch sử và một request ngoài scope.
- [ ] Stream một response ngắn, render text delta và ghi input/output/total tokens của request.
- [ ] Nêu đúng Foundry User vs Foundry Agent Consumer theo least privilege.
- [ ] Ghi Foundry Monitor estimated cost và Cost Analysis actual cost; không tạo tool, Search, compute hoặc PTU.
- [ ] Ghi quyết định giữ/xóa agent, deployment và conversations.

## 9. Practice sau lab (20–30 phút)

Không làm mock exam ngay từ đầu ngày. Sau lab, làm 8–12 câu thuộc hai nhóm:

1. agent/conversation/response, prompt vs hosted agent, tools và safeguards;
2. Foundry project, RBAC, keyless auth, model deployment type và quota.

Trả lời trước, rồi kiểm chứng **từng** đáp án bằng Microsoft Learn. Ghi một “error log” gồm: câu sai, lý do bạn chọn sai, fact Microsoft Learn xác nhận, và flashcard 1 câu. Không dùng nguồn community/exam question như nguồn chân lý vì terminology Foundry đổi nhanh.

## Sources (official first, checked 16/09/2026)

- [AI-103 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)
- [Create a prompt agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)
- [Agent, conversation and response runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components)
- [Agent Service environment setup and RBAC](https://learn.microsoft.com/en-us/azure/foundry/agents/environment-setup)
- [Microsoft Learn: Develop AI agents on Azure](https://learn.microsoft.com/en-us/training/paths/develop-ai-agents-azure/)

