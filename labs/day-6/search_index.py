"""
Day 6 preflight: verify keyless access to Azure AI Search
This intentionally performs no indexing and no model inference. It only verifies that
DefaultAzureCredential can reach the search service with the assigned search service contributor role.
"""

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

SEARCH_ENDPOINT = "https://ai103-search-index.search.windows.net"
INDEX_NAME = "ai103-rag-index"

credential = DefaultAzureCredential()
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)

# 1. Define fields for the index
fields = [
    # Unique identifier for each document
    SimpleField(name="chunk_id", type=SearchFieldDataType.STRING, key=True),
    # Metadata for filtering
    SimpleField(
        name="parent_id",
        type=SearchFieldDataType.STRING,
        filterable=True,
        retrievable=True,
    ),
    SearchableField(
        name="title", type=SearchFieldDataType.STRING, searchable=True, retrievable=True
    ),
    SimpleField(
        name="category",
        type=SearchFieldDataType.STRING,
        filterable=True,
        facetable=True,
    ),
    # Content for BM25 retrieval
    SearchableField(
        name="content",
        type=SearchFieldDataType.STRING,
        searchable=True,
        retrievable=True,
    ),
    # Embedding vector for vector search
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.SINGLE),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="my-hnsw-profile",
    ),
]

# 2. Define vector search configuration
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="my-hnsw-algo",
            parameters=HnswParameters(
                m=4,
                ef_construction=400,
                ef_search=500,
                metric="cosine",
            ),
        )
    ],
    # Define vector search profiles for the index. Each profile can specify a different algorithm configuration.
    profiles=[
        VectorSearchProfile(
            name="my-hnsw-profile",
            algorithm_configuration_name="my-hnsw-algo",
        )
    ],
)

# 3. Create the index with HNSW vector search. Semantic Ranker needs a paid tier,
# so it is intentionally omitted from this Free (F1) lab.
index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
)

index_client.create_or_update_index(index)
print(f"Index '{INDEX_NAME}' created or updated successfully.")
