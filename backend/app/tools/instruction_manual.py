import os
from mcp.server.fastmcp import FastMCP
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack import Pipeline
from typing import List

document_store = QdrantDocumentStore(
    url=os.getenv("QDRANT_URL"),
    index=os.getenv("COLLECTION_NAME"),
    embedding_dim=384,
)

query_pipeline = Pipeline()
query_pipeline.add_component(
    "text_embedder", FastembedTextEmbedder(model=os.getenv("EMBEDDING_MODEL"))
)
query_pipeline.add_component(
    "retriever", QdrantEmbeddingRetriever(document_store=document_store, top_k=2)
)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

mcp = FastMCP("Instruction Manual")


@mcp.tool()
async def retrieve_instruction_manual(query: str) -> List[str]:
    """Retrieve the instruction manual from the HVAC System Instruction Manual guide"""
    # print(query)
    result = query_pipeline.run({"text_embedder": {"text": query}})
    result = [doc.content for doc in result["retriever"]["documents"]]
    return result
