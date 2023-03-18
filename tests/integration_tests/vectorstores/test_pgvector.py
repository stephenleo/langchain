"""Test PGVector functionality."""
import os
from typing import List

from langchain.docstore.document import Document
from langchain.vectorstores.pgvector import PGVector
from tests.integration_tests.vectorstores.fake_embeddings import (
    FakeEmbeddings,
)

CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("TEST_PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get("TEST_PGVECTOR_HOST", "localhost"),
    port=int(os.environ.get("TEST_PGVECTOR_PORT", "5432")),
    database=os.environ.get("TEST_PGVECTOR_DATABASE", "postgres"),
    user=os.environ.get("TEST_PGVECTOR_USER", "postgres"),
    password=os.environ.get("TEST_PGVECTOR_PASSWORD", "postgres"),
)


ADA_TOKEN_COUNT = 1536


class FakeEmbeddingsWithAdaDimension(FakeEmbeddings):
    """Fake embeddings functionality for testing."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return simple embeddings."""
        return [[1.0] * (ADA_TOKEN_COUNT - 1) + [float(i)] for i in range(len(texts))]

    def embed_query(self, text: str) -> List[float]:
        """Return simple embeddings."""
        return [1.0] * (ADA_TOKEN_COUNT - 1) + [0.0]


def test_pgvector() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    docsearch = PGVector.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo")]


def test_pgvector_with_metadatas() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = PGVector.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo", metadata={"page": "0"})]


def test_pgvector_with_metadatas_with_scores() -> None:
    """Test end to end construction and search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": str(i)} for i in range(len(texts))]
    docsearch = PGVector.from_texts(
        texts=texts,
        collection_name="test_collection",
        embedding=FakeEmbeddingsWithAdaDimension(),
        metadatas=metadatas,
        connection_string=CONNECTION_STRING,
        pre_delete_collection=True,
    )
    output = docsearch.similarity_search_with_score("foo", k=1)
    assert output == [(Document(page_content="foo", metadata={"page": "0"}), 0.0)]
