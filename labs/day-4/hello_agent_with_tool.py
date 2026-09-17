"""
AI-103 — Day 4 Lab: Client-side Function Calling with Azure AI Foundry Agent Service.

Mental Model & Roundtrip Flow:
1. Turn 1: Client gửi câu hỏi -> Agent phân tích và sinh Tool Call Request (Function name + JSON arguments).
2. Execution: Client nhận Tool Call, tự chạy hàm Python cục bộ (không để Azure truy cập hạ tầng nội bộ).
3. Append: Client gói kết quả vào FunctionCallOutput và append vào danh sách tool_outputs.
4. Turn 2: Client gửi tool_outputs ngược lên Azure -> Agent tổng hợp và trả lời người dùng.
"""

import json
from typing import Any, Callable

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition, Tool
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputParam,
)

# ----------------------------------------------------------------------
# 1. Cấu hình kết nối Azure AI Foundry
# ----------------------------------------------------------------------
PROJECT_ENDPOINT = (
    "https://lqnhat136-8220-resource.services.ai.azure.com/"
    "api/projects/lqnhat136-8220"
)
DEPLOYMENT_NAME = "ai103-chat-mini"
AGENT_NAME = "ai103-day4-budget-tool"


def get_credential():
    """Xác thực Azure: Thử DefaultAzureCredential trước, fallback sang browser nếu cần."""
    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
        return credential
    except Exception as e:
        print(f"DefaultAzureCredential failed: {e}")
        print("Falling back to InteractiveBrowserCredential...")
        return InteractiveBrowserCredential()


# ----------------------------------------------------------------------
# 2. Định nghĩa hàm nghiệp vụ chạy Cục bộ (Client-side Function)
# ----------------------------------------------------------------------
def get_azure_budget_status(resource_group_name: str) -> str:
    """
    Hàm thực thi tại máy Client: Truy vấn dữ liệu ngân sách và chi phí thực tế.
    Dữ liệu đối soát thực tế từ checkpoint Day 3:
    - Budget: $10.00
    - Chi phí thực tế: $0.05 (Bing Services $0.04 + model inference $0.01)
    """
    if resource_group_name == "rg-ai103-lab":
        data = {
            "resource_group": "rg-ai103-lab",
            "monthly_budget_usd": 10.00,
            "actual_cost_usd": 0.05,
            "currency": "USD",
            "status": "Healthy",
            "cost_breakdown": {
                "MS Bing Services (Grounding test)": 0.04,
                "ai103-chat-mini inference": 0.01,
            },
            "note": "Lab data only; verify final billing in Azure Cost Analysis.",
        }
        return json.dumps(data, ensure_ascii=False)

    return json.dumps(
        {"error": f"Không tìm thấy dữ liệu cho resource group: {resource_group_name}"},
        ensure_ascii=False,
    )


# Bảng ánh xạ hàm (Tool Registry / Dispatcher)
TOOL_REGISTRY: dict[str, Callable[..., str]] = {
    "get_azure_budget_status": get_azure_budget_status,
}


# ----------------------------------------------------------------------
# 3. Khởi tạo Agent và Đăng ký Function Tool Schemas
# ----------------------------------------------------------------------
def setup_agent(project: AIProjectClient) -> Any:
    """Đăng ký FunctionTool và tạo/cập nhật phiên bản Agent trên Azure."""
    budget_tool = FunctionTool(
        name="get_azure_budget_status",
        description="Lấy thông tin ngân sách, chi phí thực tế và phân bổ chi phí của một Azure Resource Group.",
        parameters={
            "type": "object",
            "properties": {
                "resource_group_name": {
                    "type": "string",
                    "description": "Tên của Azure resource group, ví dụ: rg-ai103-lab",
                },
            },
            "required": ["resource_group_name"],
            "additionalProperties": False,
        },
        strict=True,  # Bắt buộc model tuân thủ chính xác JSON schema
    )

    tools: list[Tool] = [budget_tool]

    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=DEPLOYMENT_NAME,
            instructions=(
                "Bạn là trợ lý quản lý chi phí Azure thông minh. "
                "Khi người dùng hỏi về budget hoặc chi phí của bất kỳ resource group nào, "
                "bắt buộc bạn phải gọi tool `get_azure_budget_status` trước khi trả lời. "
                "Tuyệt đối không tự suy đoán số liệu. "
                "Trả lời súc tích bằng tiếng Việt (tối đa 3 câu), nêu rõ trạng thái, ngân sách và phân bổ chi phí."
            ),
            tools=tools,
        ),
    )
    print(f"[Setup] Agent '{agent.name}' (version: {getattr(agent, 'version', 'latest')}) sẵn sàng.")
    return agent


# ----------------------------------------------------------------------
# 4. Chương trình chính thực thi vòng lặp Tool Calling Roundtrip
# ----------------------------------------------------------------------
def main():
    credential = get_credential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
    openai_client = project.get_openai_client()

    agent = setup_agent(project)

    # Khởi tạo Conversation trên Azure
    conversation = openai_client.conversations.create()
    print(f"[Conversation] Đã tạo Conversation ID: {conversation.id}\n")

    user_query = "Tình trạng ngân sách và phân bổ chi phí hiện tại của nhóm rg-ai103-lab là gì?"
    print("=== [LƯỢT 1: Gửi câu hỏi đến Agent] ===")
    print(f'User Query: "{user_query}"\n')

    initial_response = openai_client.responses.create(
        conversation=conversation.id,
        input=user_query,
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
                "created_by": "user",
            }
        },
    )

    # ------------------------------------------------------------------
    # Xử lý Client-side Tool Call:
    # Model sinh function_call -> Client chạy hàm -> Append vào tool_outputs
    # ------------------------------------------------------------------
    tool_outputs: ResponseInputParam = []

    print("=== [CLIENT EXECUTION: Xử lý Tool Call từ Model] ===")
    for item in initial_response.output:
        if item.type == "function_call":
            tool_name = item.name
            tool_args_str = item.arguments
            call_id = item.call_id

            print(f"-> Model yêu cầu gọi Tool : {tool_name}")
            print(f"   Call ID                : {call_id}")
            print(f"   Arguments từ Model     : {tool_args_str}")

            tool_fn = TOOL_REGISTRY.get(tool_name)
            if not tool_fn:
                raise ValueError(f"Tool '{tool_name}' không được khai báo trong TOOL_REGISTRY.")

            # Thực thi hàm Python cục bộ tại máy client
            args_dict = json.loads(tool_args_str)
            tool_result = tool_fn(**args_dict)
            print(f"   Kết quả hàm cục bộ     : {tool_result}")

            # Đóng gói và APPEND vào danh sách tool_outputs
            tool_output_item = FunctionCallOutput(
                type="function_call_output",
                call_id=call_id,
                output=tool_result,
            )
            tool_outputs.append(tool_output_item)
            print(f"   [APPEND SUCCESS] Đã append FunctionCallOutput (call_id={call_id}) vào payload.") 
        

    if not tool_outputs:
        raise RuntimeError("Model không sinh bất kỳ function call nào! Hãy kiểm tra prompt và schema.")

    print(f"\n-> Tổng số tool outputs đã append chuẩn bị gửi lên Azure: {len(tool_outputs)}\n")

    # ------------------------------------------------------------------
    # Lượt 2: Gửi tool_outputs ngược lên Azure để Model tổng hợp kết quả
    # ------------------------------------------------------------------
    print("=== [LƯỢT 2: Submit Tool Outputs & Nhận câu trả lời cuối] ===")
    final_response = openai_client.responses.create(
        conversation=conversation.id,
        input=tool_outputs,
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
                "created_by": "user",
            }
        },
    )

    print("\n--- Final Agent Response ---")
    print(final_response.output_text)

    # Thống kê Token Usage nếu có
    if hasattr(final_response, "usage") and final_response.usage is not None:
        print("\n--- Token Usage (Turn 2) ---")
        print(f"Input tokens : {final_response.usage.input_tokens}")
        print(f"Output tokens: {final_response.usage.output_tokens}")
        print(f"Total tokens : {final_response.usage.total_tokens}")


if __name__ == "__main__":
    main()
