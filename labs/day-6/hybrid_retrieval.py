import json

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI

SEARCH_ENDPOINT = "https://ai103-search-index.search.windows.net"
INDEX_NAME = "ai103-rag-index"

RESOURCE_NAME = "lqnhat136-8220-resource"
EMBEDDING_DEPLOYMENT = "text-embedding-3-small"

QUESTION = "Khi chi phí của dự án gần chạm hạn mức, hệ thống cần làm gì?"

credential = DefaultAzureCredential()

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)

token_provider = get_bearer_token_provider(
    credential,
    "https://ai.azure.com/.default",
)

embedding_client = OpenAI(
    api_key=token_provider,
    base_url=f"https://{RESOURCE_NAME}.openai.azure.com/openai/v1/",
)
embedding_response = embedding_client.embeddings.create(
    model=EMBEDDING_DEPLOYMENT,
    input=QUESTION,
)

vector_query = VectorizedQuery(
    vector=embedding_response.data[0].embedding,
    k_nearest_neighbors=3,
    fields="content_vector",
)

results = search_client.search(
    search_text=QUESTION,
    vector_queries=[vector_query],
    select=["chunk_id", "parent_id", "title", "category", "content"],
    top=3,
)

for rank, result in enumerate(results, start=1):
    print(
        json.dumps(
            {
                "rank": rank,
                "score": result["@search.score"],
                "chunk_id": result["chunk_id"],
                "title": result["title"],
                "category": result["category"],
                "content": result["content"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )