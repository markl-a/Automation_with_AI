"""Retriever for RAG pipeline."""

from typing import List, Optional, Dict, Any, Tuple
from ai_automation_framework.core.base import BaseComponent
from ai_automation_framework.rag.embeddings import EmbeddingModel
from ai_automation_framework.rag.vector_store import VectorStore


class Retriever(BaseComponent):
    """
    Retriever for RAG (Retrieval-Augmented Generation).

    Combines embedding model and vector store for document retrieval.
    """

    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        vector_store: Optional[VectorStore] = None,
        top_k: int = 5,
        **kwargs
    ):
        """
        Initialize the retriever.

        Args:
            embedding_model: Embedding model instance
            vector_store: Vector store instance
            top_k: Number of documents to retrieve
            **kwargs: Additional configuration
        """
        super().__init__(name="Retriever", **kwargs)

        self.embedding_model = embedding_model or EmbeddingModel()
        self.vector_store = vector_store or VectorStore()
        self.top_k = top_k

    def _initialize(self) -> None:
        """Initialize the retriever."""
        self.embedding_model.initialize()
        self.vector_store.initialize()
        self.logger.info("Initialized Retriever")

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the retriever.

        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents
        """
        self.initialize()

        # Generate embeddings
        self.logger.info(f"Generating embeddings for {len(documents)} documents")
        embeddings = self.embedding_model.embed_documents(documents)

        # Store in vector store
        self.vector_store.add_documents(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Query text
            top_k: Number of documents to retrieve (overrides default)
            where: Optional metadata filters

        Returns:
            Tuple of (documents, distances, metadatas)
        """
        self.initialize()

        top_k = top_k or self.top_k

        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)

        # Search vector store
        documents, distances, metadatas = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where
        )

        self.logger.info(f"Retrieved {len(documents)} documents for query")
        return documents, distances, metadatas

    def retrieve_documents_only(
        self,
        query: str,
        top_k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Retrieve only the document texts (convenience method).

        Args:
            query: Query text
            top_k: Number of documents to retrieve
            where: Optional metadata filters

        Returns:
            List of document texts
        """
        documents, _, _ = self.retrieve(query, top_k, where)
        return documents

    def get_context_string(
        self,
        query: str,
        top_k: Optional[int] = None,
        separator: str = "\n\n---\n\n"
    ) -> str:
        """
        Get retrieved documents as a single context string.

        Args:
            query: Query text
            top_k: Number of documents to retrieve
            separator: Separator between documents

        Returns:
            Context string
        """
        documents = self.retrieve_documents_only(query, top_k)
        return separator.join(documents)
