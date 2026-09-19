from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from openai import OpenAI

SEARCH_ENDPOINT = "https://ai103-search-index.search.windows.net"
INDEX_NAME = "ai103-rag-index"

RESOURCE_NAME = "lqnhat136-8220-resource"
EMBEDDING_DEPLOYMENT = "text-embedding-3-small"


credential = DefaultAzureCredential()
search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=credential)

token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
embedding_client = OpenAI(
    api_key=token_provider,
    base_url=f"https://{RESOURCE_NAME}.openai.azure.com/openai/v1/",
)

documents = [
    {
        "chunk_id": "budget-policy-01",
        "parent_id": "azure-cost-policy.md",
        "title": "Azure Cost Policy",
        "category": "finance",
        "content": (
            "Resource group rg-ai103-lab có ngân sách 10 USD mỗi tháng. "
            "Azure Cost Management gửi cảnh báo khi mức chi tiêu đạt 80 phần trăm ngân sách."
        ),
    },
    {
        "chunk_id": "identity-policy-01",
        "parent_id": "azure-identity-policy.md",
        "title": "Keyless Authentication Policy",
        "category": "security",
        "content": (
            "Ứng dụng kết nối Azure AI Services phải ưu tiên Managed Identity "
            "hoặc DefaultAzureCredential. Không lưu API key tĩnh trong source code."
        ),
    },
    {
        "chunk_id": "search-policy-01",
        "parent_id": "azure-search-policy.md",
        "title": "Search Retrieval Policy",
        "category": "search",
        "content": (
            "Hybrid search kết hợp keyword search và vector search. "
            "Nó phù hợp khi cần vừa tìm chính xác mã lỗi, vừa hiểu ý nghĩa câu hỏi."
        ),
    },
]

embedding_response = embedding_client.embeddings.create(
    model=EMBEDDING_DEPLOYMENT,
    input=[doc["content"] for doc in documents],
)

for document, embedding in zip(documents, embedding_response.data):
    document["content_vector"] = embedding.embedding

results = search_client.upload_documents(documents=documents)
for result in results:
    print(f"Document {result.key} upload status: succeeded={result.succeeded}")

if not all(result.succeeded for result in results):
    raise RuntimeError("Some documents failed to upload. Check the logs for details.")
print("All documents uploaded successfully.")