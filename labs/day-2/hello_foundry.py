from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

RESOURCE_NAME = "lqnhat136-8220-resource"
DEPLOYMENT_NAME = "ai103-chat-mini"

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")

client = OpenAI(
    api_key=token_provider,
    base_url=f"https://{RESOURCE_NAME}.openai.azure.com/openai/v1"
)

response = client.responses.create(
    model=DEPLOYMENT_NAME,
    input="Trong đúng 2 câu tiếng việt, phân biệt giữa quota và budget trên Azure."
)

print(response.output_text)