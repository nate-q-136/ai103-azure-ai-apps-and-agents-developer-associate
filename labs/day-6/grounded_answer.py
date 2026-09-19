from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI

SEARCH_ENDPOINT = "https://ai103-search-index.search.windows.net"
INDEX_NAME = "ai103-rag-index"

RESOURCE_NAME = "lqnhat136-8220-resource"
EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
CHAT_DEPLOYMENT = "ai103-chat-mini"

QUESTION = "Khi chi phí của dự án gần chạm hạn mức, hệ thống cần làm gì?"

credential = DefaultAzureCredential()

token_provider = get_bearer_token_provider(
    credential,
    "https://ai.azure.com/.default",
)

openai_client = OpenAI(
    api_key=token_provider,
    base_url=f"https://{RESOURCE_NAME}.openai.azure.com/openai/v1/",
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)

# 1. Biến câu hỏi thành vector.
embedding_response = openai_client.embeddings.create(
    model=EMBEDDING_DEPLOYMENT,
    input=QUESTION,
)

vector_query = VectorizedQuery(
    vector=embedding_response.data[0].embedding,
    k_nearest_neighbors=2,
    fields="content_vector",
)

# 2. Hybrid retrieval: BM25 + vector.
results = list(
    search_client.search(
        search_text=QUESTION,
        vector_queries=[vector_query],
        select=["chunk_id", "parent_id", "title", "content"],
        top=2,
    )
)

# 3. Đóng gói context và citation markers.
context_blocks = []
for number, result in enumerate(results, start=1):
    context_blocks.append(
        f"""[{number}]
Title: {result["title"]}
Source: {result["parent_id"]}
Content: {result["content"]}"""
    )

context = "\n\n".join(context_blocks)

# 4. Grounded generation.
prompt = f"""Bạn là trợ lý Azure AI.

Chỉ được trả lời dựa trên CONTEXT bên dưới.
Nếu CONTEXT không đủ để trả lời, hãy nói chính xác:
"Không đủ thông tin trong tài liệu được cung cấp."

Trả lời bằng tiếng Việt, tối đa 3 câu.
Mỗi kết luận thực tế phải có citation dạng [1] hoặc [2].
Không bịa nguồn, không dùng kiến thức bên ngoài.

CONTEXT:
{context}

QUESTION:
{QUESTION}
"""

response = openai_client.responses.create(
    model=CHAT_DEPLOYMENT,
    input=prompt,
)

print("=== Grounded answer ===")
print(response.output_text)

print("\n=== Retrieved sources ===")
for number, result in enumerate(results, start=1):
    print(f"[{number}] {result['title']} — {result['parent_id']}")

if response.usage:
    print("\n=== Token usage ===")
    print(f"Input: {response.usage.input_tokens}")
    print(f"Output: {response.usage.output_tokens}")
    print(f"Total: {response.usage.total_tokens}")