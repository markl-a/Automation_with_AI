"""Embedding models for text vectorization."""

from typing import List, Optional
from openai import OpenAI
from ai_automation_framework.core.base import BaseComponent
from ai_automation_framework.core.config import get_config


class EmbeddingModel(BaseComponent):
    """
    Embedding model for converting text to vectors.

    Supports OpenAI embeddings and can be extended for other providers.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the embedding model.

        Args:
            model: Model name (default: from config)
            api_key: API key (default: from config)
            **kwargs: Additional configuration
        """
        super().__init__(name="EmbeddingModel", **kwargs)

        config = get_config()
        self.model = model or config.default_embedding_model
        self.api_key = api_key or config.openai_api_key
        self.client = None

    def _initialize(self) -> None:
        """Initialize the embedding client."""
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.logger.info(f"Initialized EmbeddingModel with {self.model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        self.initialize()

        # Validate input
        if not text or not text.strip():
            raise ValueError("Text parameter cannot be empty")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Failed to embed text: {e}")
            raise RuntimeError(f"Failed to embed text: {e}") from e

    def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Embed multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        self.initialize()

        # Validate inputs
        if not texts:
            raise ValueError("Texts parameter cannot be empty")
        if batch_size <= 0:
            raise ValueError("Batch size must be greater than 0")

        all_embeddings = []

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(embeddings)

            return all_embeddings
        except Exception as e:
            self.logger.error(f"Failed to embed texts: {e}")
            raise RuntimeError(f"Failed to embed texts: {e}") from e

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Embed documents (convenience method).

        Args:
            documents: List of documents

        Returns:
            List of embedding vectors
        """
        return self.embed_texts(documents)

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a query (convenience method).

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        return self.embed_text(query)
