import os

from haystack import Pipeline
from haystack.components.converters.txt import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
)
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


def indexing_pipeline():
    document_store = QdrantDocumentStore(
        url=os.getenv("QDRANT_URL"),
        index=os.getenv("COLLECTION_NAME"),
        embedding_dim=384,
    )

    document_embedder = FastembedDocumentEmbedder(model=os.getenv("EMBEDDING_MODEL"))

    pipeline = Pipeline()
    pipeline.add_component("converter", TextFileToDocument())
    pipeline.add_component("cleaner", DocumentCleaner())
    pipeline.add_component(
        "splitter", DocumentSplitter(split_by="word", split_length=50, split_overlap=10)
    )
    pipeline.add_component("embedder", document_embedder)
    pipeline.add_component("writer", DocumentWriter(document_store=document_store))

    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "embedder")
    pipeline.connect("embedder", "writer")

    return pipeline


def main():
    pipeline = indexing_pipeline()
    filenames = ["app/mock_instruction_manual.txt"]

    pipeline.run({"converter": {"sources": filenames}})


if __name__ == "__main__":
    main()
