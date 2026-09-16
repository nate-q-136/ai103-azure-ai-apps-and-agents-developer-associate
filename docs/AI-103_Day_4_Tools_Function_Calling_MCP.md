# AI-103 — Day 4: Tools, Function Calling & MCP

> **Mục tiêu:** Mở rộng năng lực của Prompt Agent bằng **Tools**: hiểu rõ vòng lặp Tool Calling roundtrip, tự định nghĩa **Custom Function (Client-side)**, tích hợp **OpenAPI/REST Tools**, và chuẩn **Model Context Protocol (MCP)** trong hệ sinh thái Azure AI.

**Thời lượng gợi ý:** 3–4 giờ.  
**Chi phí mục tiêu:** $0.00–$0.02 (tận dụng deployment `ai103-chat-mini` từ Day 3, tuyệt đối KHÔNG bật Bing Search, Code Interpreter hay Managed Compute).  
**Phạm vi lab:** `rg-ai103-lab` → Foundry Project `lqnhat136-8220` → deployment `ai103-chat-mini`.

---

## 1. Mental Model: Vòng lặp Tool Calling

Model AI không trực tiếp "thực thi" code hay truy vấn database từ trong não bộ của nó; nó chỉ **quyết định khi nào cần gọi tool** và **sinh tham số JSON**. Ứng dụng client hoặc agent service sẽ thực thi và gửi kết quả ngược lại cho model.

```text
[User] "Budget của rg-ai103-lab còn bao nhiêu?"
  │
  ▼
[Foundry Agent / Model]
  │  Phân tích intent & đối chiếu danh sách Tool schemas đã khai báo
  ▼
[Tool Call Request] (Model sinh: name="get_rg_budget", args={"rg_name": "rg-ai103-lab"})
  │
  ▼
[Execution Environment] (Client / Server thực thi logic hàm hoặc API)
  │  Trả về: {"budget": 10.0, "actual_cost": 0.05, "unit": "USD"}
  ▼
[Tool Call Output] Gửi kết quả ngược lại cho Agent kèm tool_call_id
  │
  ▼
[Foundry Agent / Model] Tổng hợp dữ liệu thành câu trả lời tự nhiên
  │
  ▼
[User] "Ngân sách nhóm rg-ai103-lab là $10/tháng, bạn đã sử dụng $0.05..."
```

---

## 2. Phân loại Tools trong Microsoft Foundry

Trong đề thi AI-103, Microsoft phân biệt rõ 4 nhóm Tools:

| Loại Tool | Nơi thực thi (Execution) | Chi phí / Cấu hình | Khi nào chọn trong đề thi? |
| :--- | :--- | :--- | :--- |
| **Function Tools (Custom)** | **Client-side** (Ứng dụng của bạn tự chạy code) | Miễn phí hạ tầng (chỉ tính token của model) | Cần truy vấn database nội bộ, gọi hàm Python local, hoặc bảo mật không để Azure chạm vào backend private |
| **OpenAPI / REST Tools** | **Server-side** (Agent tự gửi HTTP request) | Cần API key / OAuth, Swagger JSON spec | Kết nối trực tiếp với hệ thống SaaS có REST API chuẩn (CRM, ERP, Weather API) |
| **Built-in Tools (Azure)** | **Server-side managed** (Bing Grounding, Code Interpreter) | **Có phí riêng**: Bing ~$0.035/query; Code Interpreter tính theo compute session | Cần tra cứu web công khai hoặc cần chạy sandbox Python vẽ biểu đồ |
| **MCP (Model Context Protocol)** | **MCP Server** (Local hoặc Hosted) | Chuẩn mở do Anthropic khởi xướng, hỗ trợ qua proxy/adapter | Chuẩn hóa kho công cụ/resources dùng chung cho nhiều agent/framework |

> [!CAUTION]
> **Cảnh báo chi phí từ Day 3:** Tuyệt đối không bật toggle **Web search (Bing Grounding)** hoặc **Code Interpreter** nếu scenario không bắt buộc. Day 3 đã ghi nhận $0.04 từ Bing Services chỉ qua vài lượt test portal.

---

## 3. Kiến thức thi cốt lõi (Exam Objectives)

| Tình huống trong đề thi | Giải pháp / Lựa chọn chính xác |
| :--- | :--- |
| Agent cần lấy dữ liệu từ SQL Server on-premise an toàn | **Custom Function Tool**: Model trả về tool call, app nội bộ query DB rồi gửi kết quả lại. Không expose DB ra internet. |
| Agent cần gọi microservice nội bộ có tài liệu Swagger 2.0/3.0 | **OpenAPI Tool** trong Foundry Agent Service. |
| Model liên tục sinh tham số sai kiểu dữ liệu | Tinh chỉnh **JSON Schema** của parameters (mô tả rõ `type`, `description`, `enum`, và `required`). |
| Cần kiểm soát quyền thực thi trước khi thực sự chạy tác vụ nhạy cảm | Cấu hình cơ chế **Human-in-the-loop / Approval Flow** tại client trước khi submit tool output. |
| Phân biệt Built-in Code Interpreter vs Function Tool | Code Interpreter chạy trong **sandbox container của Azure** (có tính phí session compute); Function Tool chạy trên **máy của developer/client**. |

---

## 4. Thực hành Lab: Custom Function Calling với Python

Chúng ta sẽ tạo file `labs/day-4/function_agent.py` mở rộng từ script Day 3:
1. Định nghĩa schema hàm `get_azure_budget_status`.
2. Truyền tool definition vào Agent / Model.
3. Bắt event `response.tool_calls`, thực thi hàm giả lập và gửi kết quả trở lại conversation.

### 4.1 Schema của Tool
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_azure_budget_status",
            "description": "Lấy thông tin ngân sách và chi phí thực tế của một Resource Group trên Azure",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_group_name": {
                        "type": "string",
                        "description": "Tên của resource group cần tra cứu, ví dụ: rg-ai103-lab"
                    }
                },
                "required": ["resource_group_name"]
            }
        }
    }
]
```

### 4.2 Hàm thực thi Local (Python)
```python
import json

def get_azure_budget_status(resource_group_name: str) -> str:
    # Dữ liệu đối soát thực tế từ checkpoint Day 3
    if resource_group_name == "rg-ai103-lab":
        return json.dumps({
            "resource_group": "rg-ai103-lab",
            "monthly_budget": 10.0,
            "actual_cost": 0.05,
            "currency": "USD",
            "status": "Healthy",
            "breakdown": {"MS Bing Services": 0.04, "ai103-chat-mini inference": 0.01}
        })
    return json.dumps({"error": f"Không tìm thấy dữ liệu cho resource group {resource_group_name}"})
```

---

## 5. Model Context Protocol (MCP) trong Azure AI

MCP là chuẩn giao thức client-server giúp chuẩn hóa 3 yếu tố:
1. **Tools**: Các hành động agent có thể gọi (actions).
2. **Resources**: Dữ liệu ngữ cảnh mà agent có thể đọc (read-only data/files).
3. **Prompts**: Các mẫu prompt tái sử dụng.

Trong môi trường Azure, MCP server có thể chạy local qua `stdio` (cho developer test) hoặc qua `SSE (Server-Sent Events) / HTTP` khi deploy lên Azure Container Apps.

```text
[Foundry Agent Client]
         │ (JSON-RPC qua stdio hoặc HTTP/SSE)
         ▼
[Local / Hosted MCP Server]
   ├── Tools: [query_azure_costs, list_deployments]
   └── Resources: [docs://architecture-guidelines]
```

---

## 6. Definition of Done — Day 4

- [ ] Hiểu rõ chu trình vòng lặp Tool Calling (Prompt → Model tool call decision → Client execution → Tool output submission → Synthesis).
- [ ] Phân biệt được 4 loại tool: Function tool, OpenAPI tool, Built-in tool (Bing/Code Interpreter), và MCP server.
- [ ] Viết và chạy thành công script `labs/day-4/function_agent.py` gọi hàm custom function và nhận câu trả lời tổng hợp.
- [ ] Giải thích được tại sao Function Tool an toàn hơn cho dữ liệu private so với việc cấp quyền trực tiếp cho cloud service.
- [ ] Kiểm tra Azure Cost Analysis: xác nhận không phát sinh thêm chi phí bất thường ($0.00–$0.02).

---

## Sources (Official, checked 16/09/2026)

- [Foundry Agent Service Tools overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/)
- [Function calling in Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Microsoft Learn: Connect your agent to external tools](https://learn.microsoft.com/en-us/training/modules/develop-ai-agents-tools/)
