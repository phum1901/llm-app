from haystack import Pipeline
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
)
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.dataclasses.byte_stream import ByteStream
import requests
import os


def indexing_pipeline():
    document_store = QdrantDocumentStore(
        url=os.getenv("QDRANT_URL"),
        index="ashrae-hvac-systems-and-equipment",
        embedding_dim=384,
    )

    document_embedder = FastembedDocumentEmbedder(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )

    pipeline = Pipeline()
    pipeline.add_component("converter", PyPDFToDocument())
    pipeline.add_component("cleaner", DocumentCleaner())
    pipeline.add_component(
        "splitter", DocumentSplitter(split_by="word", split_length=64, split_overlap=4)
    )
    pipeline.add_component("embedder", document_embedder)
    pipeline.add_component("writer", DocumentWriter(document_store=document_store))

    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "embedder")
    pipeline.connect("embedder", "writer")

    return pipeline


def main():
    print("running")
    pipeline = indexing_pipeline()

    file_names = [
        "https://irancanftech.com/book/ASHRAE-HVAC-SYSTEMS-AND-EQUIPMENT-2020.pdf"
    ]
    files = []

    # Download PDF from URLs and process them
    for url in file_names:
        response = requests.get(url)
        if response.status_code == 200:
            pdf_content = response.content
            files.append(ByteStream(data=pdf_content))

    pipeline.run({"converter": {"sources": files}})


if __name__ == "__main__":
    print("running")
    main()
