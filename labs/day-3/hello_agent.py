from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

# https://<resource>.services.ai.azure.com/api/projects/<project>
PROJECT_ENDPOINT = (
    "https://lqnhat136-8220-resource.services.ai.azure.com/api/projects/lqnhat136-8220"
)
AGENT_NAME = "ai103-day3-policy-coach"


def get_credential():
    try:
        credential = DefaultAzureCredential()
        # Get credential
        credential.get_token("https://management.azure.com/.default")
        return credential
    except Exception as e:
        print(f"DefaultAzureCredential failed: {e}")
        print("Falling back to InteractiveBrowserCredential...")
        return InteractiveBrowserCredential()


# Init project client and OpenAI Client bound with agent
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=get_credential())
openai = project.get_openai_client(agent_name=AGENT_NAME)

# Create conversation on Azure
conversation = openai.conversations.create()
print(f"Created Conversation ID: {conversation.id}")

# Send the first message to the agent
response1 = openai.responses.create(
    conversation=conversation.id,
    input="Trong đúng 2 câu tiếng việt, phân biệt giữa quota và budget trên Azure.",
)
print(f"Response from agent: {response1.output_text}")
# Send follow-up message to the agent
response2 = openai.responses.create(
    conversation=conversation.id,
    input="Hãy giải thích chi tiết hơn về quota và budget trên Azure.",
)
print(f"Response from agent: {response2.output_text}")


stream = openai.responses.create(
    conversation=conversation.id,
    extra_body={
        "agent_reference": {"name": AGENT_NAME, "type": "agent_reference"},
    },
    input="Hãy dự báo giá cổ phiếu Microsoft tuần tới.",
    stream=True,
)

complete_response = ""
for event in stream:
    if event.type == "response.output_text.delta":
        complete_response += event.delta
        print(event.delta, end="", flush=True)
    elif event.type == "response.completed":
        complete_response = event.response
        break
print(f"\nFinal response from agent: {complete_response}")

print("\n")
if hasattr(complete_response, "usage") and complete_response.usage is not None:
    print(f"Input tokens:  {complete_response.usage.input_tokens}")
    print(f"Output tokens: {complete_response.usage.output_tokens}")
    print(f"Total tokens:  {complete_response.usage.total_tokens}")
