"""
Day 6 preflight: verify keyless access to Azure AI Search
This intentionally performs no indexing and no model inference. It only verifies that
DefaultAzureCredential can reach the search service with the assigned search service contributor role.
"""
import argparse
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import HnswAlgorithmConfiguration, SearchField, SearchFieldDataType, SearchIndex, SearchableField, SimpleField, VectorSearch, VectorSearchProfile



SEARCH_ENDPOINT = "https://ai103-search-index.search.windows.net"
INDEX_NAME = "ai103-rag-index"

def build_index() -> SearchIndex:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.STRING, key=True, filterable=True),
        SimpleField(name="parent_id", type=SearchFieldDataType.STRING, filterable=True, retrievable=True),
    ]
def main() -> None:
    client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=DefaultAzureCredential())
    stats = client.get_service_statistics()
    print("Keyless Azure AI Search access: OK")
    print(f"Endpoint: {SEARCH_ENDPOINT}")
    print(f"Indexes in service: {stats.counters.index_counter}")
    print(f"Document count: {stats.counters.document_counter}")

if __name__ == "__main__":
    main()
